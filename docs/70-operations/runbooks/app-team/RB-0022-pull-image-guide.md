---
id: RB-0022
title: 'App Team Runbook: Pull Image Guide'
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: not-applicable
  observability_tier: bronze
schema_version: 1
relates_to:
  - RUNBOOK_REQUEST_ECR_REGISTRY
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: runbooks
status: draft
version: '1.0'
dependencies:
  - docker
  - aws-cli
supported_until: 2028-01-05
breaking_change: false
---

# App Team Runbook: Pull Image Guide

**Audience:** Application Teams
**Purpose:** How to pull container images from ECR

---

## Quick Start

```bash
# 1. Authenticate with ECR
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.eu-west-2.amazonaws.com

# 2. Pull the image
docker pull <account-id>.dkr.ecr.eu-west-2.amazonaws.com/my-registry:latest
```

---

## Detailed Steps

### Step 1: Authenticate with ECR

```bash
aws ecr get-login-password --region eu-west-2 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.eu-west-2.amazonaws.com
```

### Step 2: Pull the Image

```bash
docker pull <account-id>.dkr.ecr.eu-west-2.amazonaws.com/my-registry:v1.2.3
```

### Step 3: Run the Image

```bash
docker run <account-id>.dkr.ecr.eu-west-2.amazonaws.com/my-registry:v1.2.3
```

---

## In Kubernetes

Update your deployment YAML:

```yaml
spec:
  containers:
    - name: my-app
      image: <account-id>.dkr.ecr.eu-west-2.amazonaws.com/my-registry:v1.2.3
```

---

## Troubleshooting

**Authentication fails:**
- Check AWS credentials are configured
- Verify you have ECR permissions

**Image not found:**
- Verify registry name and tag
- Check you have pull permissions

---

## Support

**Questions?** Contact #platform-team on Slack
