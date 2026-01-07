---
id: ADR-0085-score-implementation
title: 'ADR-0085: Implementing Score in V1'
type: adr
status: active
lifecycle: active
version: '1.0'
relates_to:
  - ADR-0085
supported_until: 2027-01-03
breaking_change: false
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
