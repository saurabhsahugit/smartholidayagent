variable "aws_region" {
  description = "AWS region for the MVP deployment. ECS Express Mode and ECR must use the same region."
  type        = string
  default     = "eu-west-2"
}

variable "project_name" {
  description = "Lowercase project name used for AWS resource names."
  type        = string
  default     = "smart-holiday-agent"
}

variable "app_image_identifier" {
  description = "Full ECR image URI and tag to deploy, for example 123456789012.dkr.ecr.eu-west-2.amazonaws.com/smart-holiday-agent:latest."
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API key used by the application."
  type        = string
  sensitive   = true
}

variable "streamlit_port" {
  description = "Container port that Streamlit listens on."
  type        = string
  default     = "8080"
}

variable "ecs_cpu" {
  description = "ECS Express Mode task CPU units. 256 is the smallest Fargate-compatible MVP size."
  type        = string
  default     = "256"
}

variable "ecs_memory" {
  description = "ECS Express Mode task memory in MiB. 512 is the smallest Fargate-compatible MVP size."
  type        = string
  default     = "512"
}

variable "min_task_count" {
  description = "Minimum number of ECS tasks to keep running for the public MVP."
  type        = number
  default     = 1
}

variable "max_task_count" {
  description = "Maximum number of ECS tasks for the public MVP."
  type        = number
  default     = 2
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days for container logs."
  type        = number
  default     = 7
}

variable "tags" {
  description = "Common tags for portfolio and cost tracking."
  type        = map(string)
  default = {
    Project     = "smart-holiday-agent"
    Environment = "mvp"
    ManagedBy   = "terraform"
  }
}
