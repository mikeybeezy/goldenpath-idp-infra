<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: APP_BUILD_PIPELINE
title: 'How It Works: Application Build Pipeline'
type: documentation
relates_to:
  - ADR-0170
  - GOV-0012-build-pipeline-standards
  - GOV-0013-devsecops-security-standards
  - GOV-0014-devsecops-implementation-matrix
  - GOV-0015-build-pipeline-testing-matrix
  - RB-0037
  - session-2026-01-19-build-pipeline-architecture
---

This guide explains the end-to-end application build and promotion pipeline.
It focuses on how CI, ECR, Argo CD Image Updater, Git write-back, and Argo CD
work together to keep Git as the source of truth.

## Overview

```text
CI (GitHub Actions) -> ECR -> Image Updater -> Git -> Argo CD -> Cluster
```

Key principles:

- **Thin app workflows** call canonical reusable workflows in the platform repo.
- **Immutable promotion** uses env-sha tags for test/staging/prod.
- **Git is source of truth** via image updater git write-back.

## High-Level Flow (AWS)

```text
      CI (GitHub Actions)
         | build + push
         v
       ECR (image tag)
         |
         v
ArgoCD Image Updater (EKS)
  - auth: GitHub App (Secrets Manager)
  - write-back: git
         |
         v
  Git Repo (new tag commit)
         |
         v
      Argo CD
  - syncs desired state
         |
         v
      EKS Deploy
```

## Local/Kind Flow (Simulation)

```text
                   ┌─────────────────────────┐
                   │     GitHub Actions      │
                   │  build/test/scan/push   │
                   └───────────┬─────────────┘
                               │
                               v
                         ┌───────────┐
                         │    ECR    │
                         │ image tags│
                         └────┬──────┘
                              │
          ┌───────────────────┴───────────────────┐
          │                                       │
          v                                       v
┌──────────────────────┐                ┌──────────────────────┐
│ Argo Image Updater   │                │ Promotion Workflow   │
│ (local/dev/prod)     │                │ (dev->test->stage->prod)
│ - detects tag/digest │                │ - re-tag in ECR       │
│ - write-back to Git  │                └──────────┬───────────┘
└──────────┬───────────┘                           │
           │                                       │
           v                                       v
      ┌───────────┐                          ┌───────────┐
      │  Git Repo │<─────────────────────────┤  Git Repo │
      │ (desired) │  tag updates committed   │ (desired) │
      └────┬──────┘                          └────┬──────┘
           │                                       │
           v                                       v
      ┌───────────┐                          ┌───────────┐
      │  Argo CD  │                          │  Argo CD  │
      │  syncs    │                          │  syncs    │
      └────┬──────┘                          └────┬──────┘
           │                                       │
           v                                       v
   ┌──────────────┐                        ┌──────────────┐
   │ Local Kind   │                        │  AWS EKS     │
   │ (simulate)   │                        │ (real env)   │
   └──────────────┘                        └──────────────┘
```

## Pipeline Stages

### 1) App Repo Calls Canonical Workflow

App repositories use a thin caller that invokes the platform workflow:

```yaml
jobs:
  build:
    uses: mikeybeezy/goldenpath-idp-infra/.github/workflows/_build-and-release.yml@main
    with:
      ecr_repository: hello-goldenpath-idp
      environment: dev
    secrets:
      AWS_ROLE_ARN: ${{ secrets.AWS_ROLE_ARN }}
```

### 2) Build, Test, Scan, Push

The canonical workflow performs:

- Gitleaks secrets scan (advisory in local/dev, blocking in test+).
- Optional tests (Python/Node/Go).
- Build and push to ECR.
- Trivy scan with blocking thresholds in test+.
- SBOM generation (required in test+).

### 3) Image Updater Watches ECR

Argo CD Image Updater polls ECR and updates Git when a new tag/digest appears.
Write-back uses a GitHub App with credentials stored in AWS Secrets Manager.

### 4) Argo CD Syncs Desired State

Argo CD reconciles the new Git commit and rolls out the deployment.
Prod is manual sync by policy; lower environments are auto-sync.

### 5) Promotion (Dev -> Test -> Staging -> Prod)

Promotion retags images in ECR to create immutable env-sha tags.
The promotion workflow enforces tag formats and uses the source tag to
derive the target tag.

## Tagging Strategy (Summary)

| Environment | Tag Format | Mutable |
|-------------|------------|---------|
| local | `:latest` | Yes |
| dev | `:latest` | Yes |
| test | `test-<sha>` | No |
| staging | `staging-<sha>` | No |
| prod | `prod-<sha>` | No |

## Git Write-Back (Summary)

- Image Updater commits tag changes to Git.
- GitHub App auth is required for AWS environments.
- Argo CD syncs from Git to the cluster.
- Local stays fast by default (digest-only, no write-back). To simulate infra-like
  behavior locally, see RB-0037 for the optional write-back toggle.

## What This Gives You

- One canonical pipeline with consistent gates across apps.
- Clear promotion path and immutable artifacts for higher environments.
- Git remains the single source of truth for deployments.

## Related Governance

- [GOV-0015 Build Pipeline Testing Matrix](../../10-governance/policies/GOV-0015-build-pipeline-testing-matrix.md)
