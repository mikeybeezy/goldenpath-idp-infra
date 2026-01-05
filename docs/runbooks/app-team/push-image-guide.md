---
id: push-image-guide
title: 'App Team Runbook: Push Image Guide'
type: runbook
category: app-team
version: '1.0'
owner: platform-team
status: draft
dependencies:
  - docker
  - aws-cli
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: not-applicable
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-05
  breaking_change: false
relates_to:
  - RUNBOOK_REQUEST_ECR_REGISTRY
---

# App Team Runbook: Push Image Guide

**Audience:** Application Teams  
**Purpose:** How to push container images to ECR

---

## Quick Start

```bash
# 1. Authenticate with ECR
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.eu-west-2.amazonaws.com

# 2. Tag your image
docker tag my-app:latest <account-id>.dkr.ecr.eu-west-2.amazonaws.com/my-registry:latest

# 3. Push
docker push <account-id>.dkr.ecr.eu-west-2.amazonaws.com/my-registry:latest
```

---

## Detailed Steps

### Step 1: Build Your Image

```bash
docker build -t my-app:latest .
```

### Step 2: Authenticate with ECR

```bash
aws ecr get-login-password --region eu-west-2 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.eu-west-2.amazonaws.com
```

### Step 3: Tag Your Image

```bash
docker tag my-app:latest \
  <account-id>.dkr.ecr.eu-west-2.amazonaws.com/my-registry:latest
```

### Step 4: Push to ECR

```bash
docker push <account-id>.dkr.ecr.eu-west-2.amazonaws.com/my-registry:latest
```

---

## Best Practices

- ✅ Use semantic versioning tags (e.g., `v1.2.3`)
- ✅ Tag with git commit SHA for traceability
- ✅ Don't rely on `latest` tag in production
- ✅ Scan images locally before pushing

---

## Troubleshooting

**Authentication fails:**
- Check AWS credentials are configured
- Verify you have ECR permissions

**Push denied:**
- Contact platform team to verify IAM permissions

---

## Support

**Questions?** Contact #platform-team on Slack
