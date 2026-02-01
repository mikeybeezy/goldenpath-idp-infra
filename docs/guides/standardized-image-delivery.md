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

## Canonical Workflow (Recommended)

The platform provides a **reusable workflow** that handles the entire build, scan, and push lifecycle with security gates built-in.

### Using the Thin Caller Template

Copy `docs/templates/workflows/delivery.yml` to your app repo's `.github/workflows/` directory:

```yaml
# .github/workflows/delivery.yml
name: Delivery Pipeline

on:
  push:
    branches: [main, development]

jobs:
  build-and-release:
    uses: mikeybeezy/goldenpath-idp-infra/.github/workflows/_build-and-release.yml@main
    with:
      environment: dev
      ecr_repository: ${{ github.event.repository.name }}
      build_context: '.'
      dockerfile_path: './Dockerfile'
    secrets: inherit
```

### What the Workflow Does

1. **Gitleaks Scan**: Detects secrets in code before build
2. **Docker Build**: Builds your image from source
3. **Trivy Scan**: Scans for vulnerabilities (blocking for test/staging/prod)
4. **SBOM Generation**: Creates software bill of materials with Syft
5. **ECR Push**: Pushes image with environment-aware tagging
6. **SARIF Upload**: Reports security findings to GitHub Security tab

### Environment-Aware Security Gates

| Environment | Gitleaks | Trivy    | SARIF Upload |
|-------------|----------|----------|--------------|
| local/dev   | Advisory | Advisory | No           |
| test+       | Blocking | Blocking | Yes          |

## Legacy Script (Local Development Only)

> **DEPRECATED**: The `ecr-build-push.sh` script is deprecated for CI use.
> Use the canonical workflow above instead.

For local development scenarios only, you can use `scripts/ecr-build-push.sh`:

```bash
./scripts/ecr-build-push.sh \
  --registry 123456789.dkr.ecr.eu-west-2.amazonaws.com \
  --name my-app \
  --sha $(git rev-parse --short HEAD) \
  --version v1.0.0
```

**Note**: This script does NOT include security scanning. Always use the canonical workflow for production builds.

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
    │ 3. Canonical Workflow         ┌────────────────────┐        │                      │
    │    _build-and-release.yml     │                    │        │                      │
    │                      │        │                    │        │                      │
    │    a. Gitleaks Scan  │        │                    │        │                      │
    │    b. Docker Build   │        │                    │        │                      │
    │    c. Trivy Scan     │        │                    │        │                      │
    │    d. SBOM Generate  │        │                    │        │                      │
    │    e. ECR Login      │───────>│   ECR API          │        │                      │
    │    f. Docker Push    │───────>│   ECR Registry     │───────>│  [IMAGE]:a1b2c3d     │
    │    g. SARIF Upload   │        │   (Layer Upload)   │        │  [IMAGE]:dev-a1b2c3d │
    │                      │        └────────────────────┘        │                      │
    └──────────────────────┘                                      └──────────────────────┘
```

## Error Handling

The process is **Strictly Atomic**. If any step fails, the entire workflow stops:

- **Security failures**: Gitleaks or Trivy findings block the build (in test/staging/prod)
- **Build failures**: Nothing is pushed if the build is broken
- **No partial images**: Prevents "dirty" or vulnerable images from appearing in the registry

## Automation Trigger

Developers don't need to run this manually. The thin caller workflow triggers automatically when:

1. **Push to development**: Builds and pushes to dev environment
2. **Push to main**: Builds and pushes to prod environment
3. **Manual dispatch**: Allows targeting specific environments

## Related Documents

- [GOV-0014: DevSecOps Implementation Matrix](../10-governance/policies/GOV-0014-devsecops-implementation-matrix.md)
- [Thin Caller Template](../templates/workflows/delivery.yml)
- [ADR-0100: Standardized ECR Lifecycle](../adrs/ADR-0100-standardized-ecr-lifecycle-and-documentation.md)
