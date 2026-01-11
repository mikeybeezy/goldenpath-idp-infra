---
id: 2026-01-04_2252_trusted-delivery-pipeline-phase-4
title: 'Implementation Plan: Phase 4 - Trusted Delivery Pipeline (ECR)'
type: implementation-plan
status: active
version: '1.0'
supported_until: '2028-01-01'
breaking_change: false
---

# Implementation Plan: Phase 4 - Trusted Delivery Pipeline (ECR)

This plan establishes a secure software supply chain by integrating AWS Elastic Container Registry (ECR) and a "Build & Push" CI workflow using a **Poly-Repo** strategy.

## User Review Required

> [!IMPORTANT]
> This change introduces a new Terraform resource (`aws_ecr_repository`) in the Platform repo and a new CI workflow in the App repo.
> **Action Required**: Ensure the GitHub Actions OIDC role (`TF_AWS_IAM_ROLE_DEV`) has permission to `ecr:GetAuthorizationToken`, `ecr:BatchCheckLayerAvailability`, `ecr:PutImage`, etc. *If not, we may need to update the role policy.*

## Proposed Changes

### [Platform Repo] (`goldenpath-idp-infra`)
#### [NEW] [envs/dev/ecr.tf](envs/dev/ecr.tf)
Create the ECR repository for the WordPress application.
- **Resource**: `aws_ecr_repository`
- **Name**: `goldenpath-wordpress-app` (Aligned with repo name)
- **Scanning**: Enabled (Scan on Push)
- **Encryption**: AES-256 (Default)

### [App Repo] (`goldenpath-wordpress-app`)
#### [NEW] [Dockerfile](file:///Users/mikesablaze/Documents/relaunch/goldenpath-wordpress-app/Dockerfile)
Create a buildable artifact for the pipeline.
- **Base**: `wordpress:latest`
- **Content**: Standard WordPress image (customizable later).

#### [NEW] [.github/workflows/ci-build-push.yml](file:///Users/mikesablaze/Documents/relaunch/goldenpath-wordpress-app/.github/workflows/ci-build-push.yml)
Create a reusable workflow to build and push images.
- **Trigger**: Push to `main`.
- **Steps**:
  1. Checkout
  2. Configure AWS Credentials (OIDC) - *Requires secrets setup in App Repo*
  3. Login to ECR
  4. Build Docker Image
  5. Push to ECR (`goldenpath-wordpress-app:latest` + commit sha)

## Verification Plan

### Automated Verification
- **Terraform Plan**: Run `terraform plan` in `envs/dev` to verify ECR creation.
- **CI Build**: Push changes to `goldenpath-wordpress-app` and verify the `Build & Push` workflow succeeds.
- **ECR Validation**: Verify the image exists in AWS ECR (via CLI or Console).

### Manual Verification
- Inspect the CI logs to ensure image security scanning is triggered.
