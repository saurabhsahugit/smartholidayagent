#!/usr/bin/env bash
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-1}"
VPC_STACK="${VPC_STACK:-smartholidayagent-vpc}"
APP_STACK="${APP_STACK:-smartholidayagent-app}"

echo "Deploying VPC stack..."
aws cloudformation deploy \
  --region "$AWS_REGION" \
  --stack-name "$VPC_STACK" \
  --template-file infra/cloudformation/vpc.yml \
  --capabilities CAPABILITY_NAMED_IAM

VpcId="$(aws cloudformation describe-stacks --region "$AWS_REGION" --stack-name "$VPC_STACK" --query "Stacks[0].Outputs[?OutputKey=='VpcId'].OutputValue" --output text)"
PublicSubnet1Id="$(aws cloudformation describe-stacks --region "$AWS_REGION" --stack-name "$VPC_STACK" --query "Stacks[0].Outputs[?OutputKey=='PublicSubnet1Id'].OutputValue" --output text)"
PublicSubnet2Id="$(aws cloudformation describe-stacks --region "$AWS_REGION" --stack-name "$VPC_STACK" --query "Stacks[0].Outputs[?OutputKey=='PublicSubnet2Id'].OutputValue" --output text)"

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/smartholidayagent"
IMAGE_TAG="$(git rev-parse --short HEAD)"
IMAGE_URI="${ECR_URI}:${IMAGE_TAG}"

echo "Deploying app stack (creates ECR repo, ECS, ALB)..."
aws cloudformation deploy \
  --region "$AWS_REGION" \
  --stack-name "$APP_STACK" \
  --template-file infra/cloudformation/app.yml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    VpcId="$VpcId" \
    PublicSubnet1Id="$PublicSubnet1Id" \
    PublicSubnet2Id="$PublicSubnet2Id" \
    ImageUri="$IMAGE_URI"

echo "Logging in to ECR..."
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "Building image..."
docker build -t smartholidayagent:"$IMAGE_TAG" .
docker tag smartholidayagent:"$IMAGE_TAG" "$IMAGE_URI"

echo "Pushing image..."
docker push "$IMAGE_URI"

echo "Updating service to new image..."
aws cloudformation deploy \
  --region "$AWS_REGION" \
  --stack-name "$APP_STACK" \
  --template-file infra/cloudformation/app.yml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    VpcId="$VpcId" \
    PublicSubnet1Id="$PublicSubnet1Id" \
    PublicSubnet2Id="$PublicSubnet2Id" \
    ImageUri="$IMAGE_URI"

ALB_DNS="$(aws cloudformation describe-stacks --region "$AWS_REGION" --stack-name "$APP_STACK" --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue" --output text)"
echo "Deployed. URL: http://${ALB_DNS}"