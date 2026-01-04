---
id: 27_CI_IMAGE_SCANNING
title: CI Image Scanning (Living Document)
type: documentation
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to: []
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
