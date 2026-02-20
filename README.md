## Deploy to AWS (CloudFormation + ECS Fargate)

Prereqs:
- AWS CLI authenticated
- Docker installed
- Permissions to create: CloudFormation stacks, IAM roles, ECR, ECS, ALB, EC2 networking

Deploy:
```bash
export AWS_REGION=us-east-1
./scripts/deploy_aws.sh
```

This will:
- create a small VPC (2 public subnets)
- create ECS Fargate service behind an ALB
- build & push the container to ECR
- update the service to run the new image