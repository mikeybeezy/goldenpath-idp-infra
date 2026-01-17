---
id: standardized-image-delivery
title: Standardized Image Delivery Guide
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - CL-0062-documentation-generator-metadata-compliance
---
# Standardized Image Delivery Guide

## Overview
This guide explains our "Golden Path" for delivery: how application teams build and push container images to Elastic Container Registry (ECR).

## The Build & Push Tool
To keep things simple, the platform provides a single script: `ecr-build-push.sh`. Instead of developers writing complex deployment logic, they use this one tool to handle the entire lifecycle.

### What the tool does
1.  **Auto-Login**: Securely authenticates with AWS without needing manual passwords.
2.  **Reliable Building**: It builds your Docker image from your source code.
3.  **Dual Tagging**: It tags every image twice:
    *   **Git SHA**: For technical tracking (exactly which code is inside).
    *   **Version**: For human tracking (e.g., `1.0.5`).
4.  **Streaming**: It pushes the finished image to the centralized registry.

## Security (OIDC)
We use **OpenID Connect (OIDC)** for all automated builds. This is a "secretless" system—we don't store long-lived password keys in GitHub. Instead, AWS and GitHub "trust" each other for a few minutes while the build is running.

### How it works in CI
```text
      GITHUB ACTIONS (CI)             AWS CLOUD (TRUST)             AWS ECR (STORAGE)
    ┌──────────────────────┐        ┌────────────────────┐        ┌──────────────────────┐
    │                      │        │                    │        │                      │
    │ 1. Request OIDC JWT  ├───────>│  AWS STS / IAM     │        │                      │
    │    (id-token: write) │        │  Check Trust Rel.  │        │                      │
    │                      │        │                    │        │                      │
    │ 2. Receive Temp Creds│<───────┤  Assume Role ARN   │        │                      │
    │    (Secretless!)     │        │                    │        │                      │
    │                      │        └────────────────────┘        │                      │
    │                      │                                      │                      │
    │ 3. Run Platform Script        ┌────────────────────┐        │                      │
    │    (ecr-build-push.sh)        │                    │        │                      │
    │                      │        │                    │        │                      │
    │    a. Get Login Token│───────>│   ECR API          │        │                      │
    │    b. Docker Login   │<───────┤   (Login Auth)     │        │                      │
    │                      │        │                    │        │                      │
    │    c. Docker Build   │        └────────────────────┘        │                      │
    │    d. Docker Tag     │                                      │                      │
    │       (SHA + Ver)    │                                      │                      │
    │                      │        ┌────────────────────┐        │                      │
    │    e. Docker Push    │───────>│   ECR Registry     │───────>│  [IMAGE]:a1b2c3d     │
    │                      │        │   (Layer Upload)   │        │  [IMAGE]:1.2.0       │
    │                      │        └────────────────────┘        │                      │
    └──────────────────────┘                                      └──────────────────────┘
```

## GitHub Actions Integration
This mapping shows how the OIDC security flow and the build script work together in your application's CI pipeline.

```yaml
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      id-token: write # Required for OIDC
      contents: read
    steps:
      - uses: actions/checkout@v4

      # 1. Start the OIDC Trust session with AWS
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/my-app-pusher
          aws-region: eu-west-2

      # 2. Run the one-step build and push tool
      - name: Build and Push
        run: |
          ./scripts/ecr-build-push.sh \
            --registry 123456789.dkr.ecr.eu-west-2.amazonaws.com \
            --name my-app \
            --sha ${{ github.sha }} \
            --version ${{ github.ref_name }} # e.g. v1.0.0
```

## Error Handling
The process is **Strictly Atomic**. If any step fails (like a syntax error in your code or a connection issue), the entire process stops immediately.
*   **Nothing is pushed** if the build is broken.
*   This prevents "dirty" or partial images from ever appearing in the registry.

## Automation Trigger
Developers don't need to run this manually. It is designed to trigger automatically when:
1.  **Merging**: When code is merged to the `main` branch.
2.  **Tagging**: When a developer creates a new Release version in Git.
