data "aws_iam_policy_document" "ecs_tasks_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "ecs_infrastructure_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs.amazonaws.com"]
    }
  }
}

resource "aws_ecr_repository" "app" {
  name                 = var.project_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = var.tags
}

resource "aws_secretsmanager_secret" "openai_api_key" {
  name                    = "${var.project_name}/openai-api-key"
  recovery_window_in_days = 7

  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "openai_api_key_value" {
  secret_id     = aws_secretsmanager_secret.openai_api_key.id
  secret_string = var.openai_api_key
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/express/${var.project_name}"
  retention_in_days = var.log_retention_days

  tags = var.tags
}

resource "aws_iam_role" "ecs_execution" {
  name               = "${var.project_name}-ecs-execution"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_assume_role.json

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_infrastructure" {
  name               = "${var.project_name}-ecs-infrastructure"
  assume_role_policy = data.aws_iam_policy_document.ecs_infrastructure_assume_role.json

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ecs_infrastructure" {
  role       = aws_iam_role.ecs_infrastructure.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSInfrastructureRoleforExpressGatewayServices"
}

resource "aws_iam_role" "ecs_task" {
  name               = "${var.project_name}-ecs-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_assume_role.json

  tags = var.tags
}

data "aws_iam_policy_document" "openai_secret_access" {
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.openai_api_key.arn]
  }
}

resource "aws_iam_role_policy" "ecs_execution_secret_access" {
  name   = "${var.project_name}-execution-secret-access"
  role   = aws_iam_role.ecs_execution.id
  policy = data.aws_iam_policy_document.openai_secret_access.json
}

resource "aws_iam_role_policy" "ecs_task_secret_access" {
  name   = "${var.project_name}-task-secret-access"
  role   = aws_iam_role.ecs_task.id
  policy = data.aws_iam_policy_document.openai_secret_access.json
}

resource "aws_ecs_express_gateway_service" "app" {
  service_name            = var.project_name
  execution_role_arn      = aws_iam_role.ecs_execution.arn
  infrastructure_role_arn = aws_iam_role.ecs_infrastructure.arn
  task_role_arn           = aws_iam_role.ecs_task.arn

  cpu                     = var.ecs_cpu
  memory                  = var.ecs_memory
  health_check_path       = "/"
  wait_for_steady_state   = true

  primary_container {
    image          = var.app_image_identifier
    container_port = tonumber(var.streamlit_port)

    aws_logs_configuration {
      log_group         = aws_cloudwatch_log_group.app.name
      log_stream_prefix = "streamlit"
    }

    environment {
      name  = "STREAMLIT_SERVER_PORT"
      value = var.streamlit_port
    }

    environment {
      name  = "STREAMLIT_SERVER_ADDRESS"
      value = "0.0.0.0"
    }

    secret {
      name       = "OPENAI_API_KEY"
      value_from = aws_secretsmanager_secret.openai_api_key.arn
    }
  }

  scaling_target {
    auto_scaling_metric       = "AVERAGE_CPU"
    auto_scaling_target_value = 70
    min_task_count            = var.min_task_count
    max_task_count            = var.max_task_count
  }

  tags = var.tags
}
