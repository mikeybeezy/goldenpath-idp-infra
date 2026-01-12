---
id: 27_CI_IMAGE_SCANNING
title: CI Image Scanning (Living Document)
type: documentation
risk_profile:
  production_impact: medium
  security_risk: high
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 1
relates_to:
  - ADR-0023
  - 22_CONTAINER_REGISTRY_STANDARD
  - CI_WORKFLOWS
category: security
supported_until: 2028-01-01
version: 1.0
dependencies:
  - module:trivy
breaking_change: false
---

# CI Image Scanning (Living Document)

This document describes the default image scanning approach in CI.

## Default scanner

- Trivy

## Gate policy

- Prod: fail on HIGH/CRITICAL.
- Dev/test: warn on HIGH/CRITICAL.

## Optional layers

- ECR enhanced scanning (continuous registry scanning).
- Docker Scout (if licensing and org setup allow).

## Implementation notes

- Scan can run before push (local image) or after push (registry image).
- Keep DB updates in CI to avoid stale results.
- Keep thresholds configurable per environment.

## Change process

- Update ADR if policy or tool changes.
- Keep this doc aligned with CI workflows.
