output "ecr_repository_url" {
  description = "ECR repository URL to build, tag, and push the Streamlit image."
  value       = aws_ecr_repository.app.repository_url
}

output "openai_secret_arn" {
  description = "Secrets Manager ARN for the OpenAI API key; populate it with aws secretsmanager put-secret-value before deploying ECS Express Mode."
  value       = aws_secretsmanager_secret.openai_api_key.arn
}

output "ecs_express_service_url" {
  description = "Public ECS Express Mode URL for the deployed Smart Holiday Agent."
  value       = aws_ecs_express_gateway_service.app.ingress_paths[0].endpoint
}
