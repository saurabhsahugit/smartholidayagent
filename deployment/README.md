# Deployment Directory


| Decision | MVP choice | Why |
| --- | --- | --- |
| Runtime | AWS App Runner | Managed container hosting with fewer moving parts than ECS for a Streamlit app. No cold starts |
| IaC | Terraform | More wider application than AWS CDK |
| Image registry | Amazon ECR | Native private image source for App Runner. |
| Secrets | AWS Secrets Manager | Keeps `OPENAI_API_KEY` out of Git, Docker images, and Terraform variables. |
| Cost posture | Smallest App Runner instance | Starts with `0.25 vCPU` and `0.5 GB`; destroy when not demoing. |
