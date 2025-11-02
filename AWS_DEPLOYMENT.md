# 🚀 AWS Fargate Deployment Guide

Deploy your Remote Browser Streaming system to AWS Fargate for production use.

---

## 📋 Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Docker installed locally
- Domain name (optional, but recommended)

---

## 🏗️ Architecture Overview

```
Internet → ALB → ECS Fargate Tasks → Chrome + WebRTC Server
                    ↓
                 ECR (Container Registry)
```

**Components:**
- **Application Load Balancer (ALB)** - Routes traffic and handles WebSocket connections
- **ECS Fargate** - Runs containerized browser streaming application
- **ECR** - Stores Docker images
- **CloudWatch** - Logs and monitoring
- **Route 53** (optional) - DNS management
- **ACM** (optional) - SSL/TLS certificates

---

## Step 1: Build and Push Docker Image

### 1.1 Build Docker Image Locally

```bash
# Build image
docker build -t remote-browser:latest .

# Test locally
docker run -p 5000:5000 remote-browser:latest

# Verify at http://localhost:5000
```

### 1.2 Create ECR Repository

```bash
# Create repository
aws ecr create-repository \
    --repository-name remote-browser \
    --region us-east-1

# Get repository URI (save this)
aws ecr describe-repositories \
    --repository-names remote-browser \
    --region us-east-1 \
    --query 'repositories[0].repositoryUri' \
    --output text
```

### 1.3 Authenticate Docker to ECR

```bash
# Get login password and authenticate
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
```

### 1.4 Tag and Push Image

```bash
# Tag image
docker tag remote-browser:latest \
    <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/remote-browser:latest

# Push to ECR
docker push \
    <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/remote-browser:latest
```

---

## Step 2: Create ECS Cluster

### 2.1 Create Cluster

```bash
aws ecs create-cluster \
    --cluster-name remote-browser-cluster \
    --region us-east-1
```

### 2.2 Create Task Execution Role

Create IAM role for ECS tasks:

```bash
# Create trust policy file
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
    --role-name ecsTaskExecutionRole \
    --assume-role-policy-document file://trust-policy.json

# Attach policy
aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

---

## Step 3: Create Task Definition

Create `task-definition.json`:

```json
{
  "family": "remote-browser-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "executionRoleArn": "arn:aws:iam::<YOUR_AWS_ACCOUNT_ID>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "remote-browser",
      "image": "<YOUR_AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/remote-browser:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "PYTHONUNBUFFERED",
          "value": "1"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/remote-browser",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:5000/health')\" || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      },
      "linuxParameters": {
        "sharedMemorySize": 2048
      }
    }
  ]
}
```

Register task definition:

```bash
# Create CloudWatch log group first
aws logs create-log-group --log-group-name /ecs/remote-browser

# Register task definition
aws ecs register-task-definition \
    --cli-input-json file://task-definition.json
```

---

## Step 4: Create Application Load Balancer

### 4.1 Create Security Groups

```bash
# ALB Security Group
aws ec2 create-security-group \
    --group-name remote-browser-alb-sg \
    --description "Security group for ALB" \
    --vpc-id <YOUR_VPC_ID>

# Allow HTTP/HTTPS
aws ec2 authorize-security-group-ingress \
    --group-id <ALB_SG_ID> \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id <ALB_SG_ID> \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# ECS Tasks Security Group
aws ec2 create-security-group \
    --group-name remote-browser-ecs-sg \
    --description "Security group for ECS tasks" \
    --vpc-id <YOUR_VPC_ID>

# Allow traffic from ALB
aws ec2 authorize-security-group-ingress \
    --group-id <ECS_SG_ID> \
    --protocol tcp \
    --port 5000 \
    --source-group <ALB_SG_ID>
```

### 4.2 Create ALB

```bash
# Create ALB
aws elbv2 create-load-balancer \
    --name remote-browser-alb \
    --subnets <SUBNET_ID_1> <SUBNET_ID_2> \
    --security-groups <ALB_SG_ID> \
    --scheme internet-facing \
    --type application \
    --ip-address-type ipv4
```

### 4.3 Create Target Group

```bash
# Create target group
aws elbv2 create-target-group \
    --name remote-browser-tg \
    --protocol HTTP \
    --port 5000 \
    --vpc-id <YOUR_VPC_ID> \
    --target-type ip \
    --health-check-path /health \
    --health-check-interval-seconds 30 \
    --health-check-timeout-seconds 5 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3
```

### 4.4 Create Listener

```bash
# Create HTTP listener
aws elbv2 create-listener \
    --load-balancer-arn <ALB_ARN> \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=<TARGET_GROUP_ARN>
```

---

## Step 5: Create ECS Service

```bash
aws ecs create-service \
    --cluster remote-browser-cluster \
    --service-name remote-browser-service \
    --task-definition remote-browser-task \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_ID_1>,<SUBNET_ID_2>],securityGroups=[<ECS_SG_ID>],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=<TARGET_GROUP_ARN>,containerName=remote-browser,containerPort=5000"
```

---

## Step 6: Configure Auto Scaling (Optional)

### 6.1 Register Scalable Target

```bash
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --scalable-dimension ecs:service:DesiredCount \
    --resource-id service/remote-browser-cluster/remote-browser-service \
    --min-capacity 1 \
    --max-capacity 10
```

### 6.2 Create Scaling Policy

```bash
aws application-autoscaling put-scaling-policy \
    --service-namespace ecs \
    --scalable-dimension ecs:service:DesiredCount \
    --resource-id service/remote-browser-cluster/remote-browser-service \
    --policy-name cpu-scaling-policy \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

Create `scaling-policy.json`:

```json
{
  "TargetValue": 70.0,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
  },
  "ScaleInCooldown": 300,
  "ScaleOutCooldown": 60
}
```

---

## Step 7: SSL/TLS Setup (Optional but Recommended)

### 7.1 Request Certificate

```bash
aws acm request-certificate \
    --domain-name browser.yourdomain.com \
    --validation-method DNS \
    --region us-east-1
```

### 7.2 Add HTTPS Listener

```bash
aws elbv2 create-listener \
    --load-balancer-arn <ALB_ARN> \
    --protocol HTTPS \
    --port 443 \
    --certificates CertificateArn=<CERTIFICATE_ARN> \
    --default-actions Type=forward,TargetGroupArn=<TARGET_GROUP_ARN>
```

---

## Step 8: Domain Configuration (Optional)

### 8.1 Create Route 53 Record

```bash
# Get ALB DNS name
aws elbv2 describe-load-balancers \
    --load-balancer-arns <ALB_ARN> \
    --query 'LoadBalancers[0].DNSName' \
    --output text

# Create alias record (via console or CLI)
aws route53 change-resource-record-sets \
    --hosted-zone-id <HOSTED_ZONE_ID> \
    --change-batch file://record-change.json
```

---

## 📊 Monitoring and Logging

### View Logs

```bash
# Stream logs
aws logs tail /ecs/remote-browser --follow
```

### CloudWatch Metrics

Monitor:
- CPU utilization
- Memory utilization
- Network traffic
- Task count
- Health check status

### Set Up Alarms

```bash
aws cloudwatch put-metric-alarm \
    --alarm-name remote-browser-high-cpu \
    --alarm-description "Alert when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2
```

---

## 💰 Cost Estimation (us-east-1)

**Monthly costs (approximate):**

- **Fargate (2 vCPU, 4GB RAM):**
  - 2 tasks running 24/7: ~$100-150/month
- **ALB:** ~$20-30/month
- **Data Transfer:** Variable based on usage
- **CloudWatch Logs:** ~$5-10/month
- **ECR Storage:** ~$1/month

**Total:** ~$130-200/month for minimal setup

**Cost Optimization:**
- Use spot instances for non-production
- Scale down during off-peak hours
- Use reserved capacity for predictable workloads

---

## 🔒 Security Best Practices

1. **Use HTTPS** - Always use SSL/TLS certificates
2. **Enable WAF** - Protect against common web exploits
3. **Restrict Access** - Use security groups and NACLs
4. **Authentication** - Add authentication layer (Cognito, OAuth)
5. **Logging** - Enable all CloudWatch logs
6. **Secrets** - Use AWS Secrets Manager for sensitive data
7. **IAM Roles** - Use least privilege principle
8. **VPC** - Deploy in private subnets when possible

---

## 🧪 Testing Deployment

```bash
# Get ALB DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --load-balancer-arns <ALB_ARN> \
    --query 'LoadBalancers[0].DNSName' \
    --output text)

# Test health endpoint
curl http://$ALB_DNS/health

# Open in browser
echo "http://$ALB_DNS"
```

---

## 🔄 Updating Deployment

### Update Container Image

```bash
# Build new image
docker build -t remote-browser:latest .

# Tag with version
docker tag remote-browser:latest \
    <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/remote-browser:v2

# Push to ECR
docker push \
    <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/remote-browser:v2

# Update task definition and service
aws ecs update-service \
    --cluster remote-browser-cluster \
    --service remote-browser-service \
    --force-new-deployment
```

---

## 🗑️ Cleanup

```bash
# Delete service
aws ecs delete-service \
    --cluster remote-browser-cluster \
    --service remote-browser-service \
    --force

# Delete cluster
aws ecs delete-cluster --cluster remote-browser-cluster

# Delete ALB
aws elbv2 delete-load-balancer --load-balancer-arn <ALB_ARN>

# Delete target group
aws elbv2 delete-target-group --target-group-arn <TARGET_GROUP_ARN>

# Delete ECR repository
aws ecr delete-repository \
    --repository-name remote-browser \
    --force
```

---

## 📞 Troubleshooting

### Tasks Not Starting

- Check CloudWatch logs
- Verify security groups allow traffic
- Ensure sufficient vCPU/memory limits
- Check ECR image permissions

### Health Checks Failing

- Verify `/health` endpoint responds
- Check security group rules
- Increase health check grace period

### High Latency

- Deploy in multiple regions
- Use CloudFront CDN
- Optimize container size
- Scale horizontally

---

## ✅ Deployment Checklist

- [ ] Docker image built and tested locally
- [ ] ECR repository created
- [ ] Image pushed to ECR
- [ ] ECS cluster created
- [ ] Task definition registered
- [ ] Security groups configured
- [ ] ALB created and configured
- [ ] Target group created
- [ ] ECS service created
- [ ] Auto-scaling configured (optional)
- [ ] SSL certificate requested (optional)
- [ ] HTTPS listener added (optional)
- [ ] Domain configured (optional)
- [ ] CloudWatch alarms set up
- [ ] Tested health endpoint
- [ ] Tested WebRTC streaming

---

**Ready for production! 🚀**

Your Remote Browser Streaming system is now running on AWS Fargate!

