# Argo CD Image Updater

Argo CD Image Updater automates image tag updates in GitOps repositories.

## Overview

Image Updater watches container registries (ECR) for new image tags and
automatically commits updates to Git, triggering Argo CD sync.

## Deployment Architecture

```text
┌─────────────────────────────────────────────────────────────────────┐
│                  IMAGE UPDATE FLOW                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  CI Pipeline ──► ECR Push ──► Image Updater ──► Git Commit ──► Argo │
│                                     │                                │
│                              Watches tags                            │
│                              Commits to Git                          │
│                                                                      │
│  Environment Sync Policies:                                          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐          │
│  │   DEV   │    │  TEST   │    │ STAGING │    │  PROD   │          │
│  │  auto   │    │  auto   │    │  auto   │    │ MANUAL  │          │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Update Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `latest` | Always use most recent tag | dev/test |
| `semver` | Follow semantic versioning | staging/prod |
| `digest` | Pin exact image digest | security-critical |

## Configuration per Environment

### Dev/Test - Latest Tags

```yaml
argocd-image-updater.argoproj.io/image-list: app=<ecr-repo>
argocd-image-updater.argoproj.io/app.update-strategy: latest
```

### Staging/Prod - Semantic Versioning

```yaml
argocd-image-updater.argoproj.io/image-list: app=<ecr-repo>
argocd-image-updater.argoproj.io/app.update-strategy: semver
argocd-image-updater.argoproj.io/app.allow-tags: regexp:^v\d+\.\d+\.\d+$
```

## ECR Authentication

Image Updater requires ECR credentials to pull image metadata.

### Option 1: IRSA (Recommended for EKS)

Service account annotated with IAM role for ECR read access.

### Option 2: Secrets

ECR credentials stored in Kubernetes secret.

## Write-back Methods

| Method | Description | Recommendation |
|--------|-------------|----------------|
| `git` | Commits directly to repo | Recommended |
| `argocd` | Updates via Argo CD API | Fallback |

## Files

- `values/dev.yaml` - Dev environment configuration
- `values/test.yaml` - Test environment configuration
- `values/staging.yaml` - Staging environment configuration
- `values/prod.yaml` - Production environment configuration

## Related

- [ADR-0172: CD Promotion Strategy](../../docs/adrs/ADR-0172-cd-promotion-strategy-with-approval-gates.md)
- [Argo CD Image Updater Docs](https://argocd-image-updater.readthedocs.io/)
