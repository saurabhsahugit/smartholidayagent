variable "aws_region" {
  description = "AWS region for the MVP deployment. App Runner and ECR must use the same region."
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

variable "tags" {
  description = "Common tags for portfolio and cost tracking."
  type        = map(string)
  default = {
    Project     = "smart-holiday-agent"
    Environment = "mvp"
    ManagedBy   = "terraform"
  }
}
