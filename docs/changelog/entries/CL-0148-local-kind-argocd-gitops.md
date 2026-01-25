<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0148
title: Local Kind Cluster with Argo CD GitOps
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to:
  - ADR-0055-platform-tempo-tracing-backend
  - ADR-0171-platform-application-packaging-strategy
  - ADR-0172-cd-promotion-strategy-with-approval-gates
  - EC-0006-competitor-analysis-tap
  - EC-0007-kpack-buildpacks-integration
  - session-2026-01-18-secrets-lifecycle
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-18
author: platform-team
---

# CL-0148: Local Kind Cluster with Argo CD GitOps

## Summary

Complete local development environment with Argo CD GitOps, App-of-Apps
bootstrap pattern, and hello-goldenpath-idp deployment validation.

## Changes

### Added

- **App-of-Apps Bootstrap**: `gitops/argocd/bootstrap/local-app-of-apps.yaml`
  - Single manifest deploys all local applications
  - Sync waves for ordered deployment
- **Argo CD Image Updater**: Helm values for all environments (dev/test/staging/prod)
  - ECR registry integration with correct account ID (593517239005)
  - Git write-back configuration
- **Tempo Tracing**: Argo CD Applications for distributed tracing
- **ECR Scripts**:
  - `scripts/refresh-ecr-secret.sh` - Refresh ECR pull secrets
  - `scripts/load-image-to-kind.sh` - Load images to Kind cluster
- **Documentation**:
  - ADR-0171: Platform Application Packaging Strategy
  - ADR-0172: CD Promotion Strategy with Approval Gates
  - EC-0006: VMware TAP Competitor Analysis
  - EC-0007: kpack and Cloud Native Buildpacks Integration

### Changed

- Fixed ECR account ID from 339712971032 to 593517239005 across codebase
- Updated local Argo CD apps to use `development` branch
- Updated Backstage app to use multi-source pattern with official Helm chart

### Validation

- Argo CD installed with 7 pods healthy
- hello-goldenpath-idp deployed and health check verified
- ECR pull secrets working with correct registry

## Migration

No migration required. New features for local development.
