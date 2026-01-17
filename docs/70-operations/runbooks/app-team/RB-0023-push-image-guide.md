---
id: RB-0023-push-image-guide
title: 'App Team Runbook: Push Image Guide'
type: runbook
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: not-applicable
  observability_tier: bronze
  maturity: 1
relates_to:
  - DOCS_RUNBOOKS_README
  - RUNBOOK_REQUEST_ECR_REGISTRY
status: draft
category: runbooks
supported_until: 2028-01-05
version: '1.0'
dependencies:
  - docker
  - aws-cli
breaking_change: false
---
# App Team Runbook: Push Image Guide

**Audience:** Application Teams
**Purpose:** How to push container images to ECR

---

## Quick Start (Recommended)

The platform provide a standardized script to handle authentication, building, tagging, and pushing in one command:

```bash
./scripts/ecr-build-push.sh \
  --registry <account-id>.dkr.ecr.eu-west-2.amazonaws.com \
  --name my-app \
  --sha $(git rev-parse --short HEAD) \
  --version 1.0.0
```

---

## Manual Steps

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

## GitHub Actions Integration (OIDC)

For secure, keyless authentication in GitHub Actions, use OIDC with the `aws-actions/configure-aws-credentials` action before running the script:

```yaml
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      id-token: write # Required for OIDC
      contents: read
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::<account-id>:role/<app-role-name>
          aws-region: eu-west-2

      - name: Build and Push
        run: |
          ./scripts/ecr-build-push.sh \
            --registry <account-id>.dkr.ecr.eu-west-2.amazonaws.com \
            --name my-app \
            --sha ${{ github.sha }}
```

---

## Best Practices

- ✅ **Use OIDC**: Never use long-lived IAM Secret Keys.
- ✅ **Least Privilege**: Ensure the assumed role only has permissions for its specific repository.
- ✅ **Standard Tooling**: Always use `ecr-build-push.sh` to ensure consistent tagging.
- ✅ **SHAs over Latest**: Use Git SHAs for production deployments to ensure immutability.

---

## Troubleshooting

**Authentication fails:**
- Verify `id-token: write` permission is present in the workflow.
- Check that the OIDC Trust Relationship on the IAM Role allows your repository and branch.
- Ensure the `aws-region` matches the registry region.

---

## Support

**Questions?** Contact #platform-team on Slack
