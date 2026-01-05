---
id: 22_CONTAINER_REGISTRY_STANDARD
title: Container Registry Standard (Living Document)
type: documentation
category: 60-security
version: 1.0
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: medium
  security_risk: medium
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - ADR-0018
  - 27_CI_IMAGE_SCANNING
---

# Container Registry Standard (Living Document)

This document captures the current registry approach and implementation details.
It should evolve as the platform matures.

## Current stance

- Default registry: Amazon ECR
- Supported alternative: GHCR
- Docker Hub: allowed for public base images, discouraged as primary registry

## Rationale (short)

- ECR aligns with AWS-first, private EKS networking and reduces NAT/egress cost.
- IAM and OIDC provide clean auth for CI and node pulls.
- Deterministic rebuilds benefit from fewer external dependencies.

## Current implementation (V1)

- Platform-owned images (Backstage, reference apps) publish to ECR by default.
- Registry URL is configurable per environment; avoid hardcoding in charts.
- CI should support pushing to ECR and GHCR.

## Scanning guidance

- CI scan (Trivy/Grype) for shift-left gating.
- Registry scan (ECR scanning) for continuous CVE detection.

## Exceptions

Teams may use GHCR (or another registry) when:

- the workload is public or OSS,
- GitHub-native workflows are a priority,
- the environment is non-AWS.

## Change process

- Update ADR if default registry changes.
- Update governance and this living document when implementation shifts.
