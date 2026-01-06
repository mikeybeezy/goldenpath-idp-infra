---
id: ADR-0085
title: 'ADR-0085: Implementing Score in V1'
type: adr
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2027-01-03
  breaking_change: false
relates_to:
  - ADR-0085
---

# ADR-0085: Implementing Score in V1

## Context
Our current IDP handles application scaffolding via Backstage Templates that generate standard Kubernetes manifests. While functional, this "bakes in" the platform's K8s logic into every developers branch at creation time.

## Decision
We recommend **skipping Score for the V1 MVP** and targeting it for **V1.1 or V2**.

## Status
Proposed

## Consequences
- **Positive**: Reduced initial integration risk and faster time-to-market for V1.
- **Negative**: Requires a migration path from standard YAML to Score in the future.
- **Neutral**: Keeps the current Backstage-to-Manifest flow as the primary "Golden Path" for now.
