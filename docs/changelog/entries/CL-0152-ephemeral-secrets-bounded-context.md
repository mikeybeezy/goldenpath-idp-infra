---
id: CL-0152
title: Ephemeral Secrets Bounded Context Isolation
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - envs/dev/main.tf
  - modules/aws_rds/secrets.tf
  - modules/aws_rds/variables.tf
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
schema_version: 1
relates_to:
  - ADR-0006-platform-secrets-strategy
  - session_capture/2026-01-20-persistent-cluster-deployment
supersedes: []
superseded_by: []
tags:
  - secrets
  - ephemeral
  - bounded-context
  - rds
inheritance: {}
value_quantification:
  vq_class: 🟢 HV/HQ
  impact_tier: medium
  potential_savings_hours: 4.0
supported_until: 2028-01-20
date: 2026-01-20
author: platform-team
---

# Ephemeral Secrets Bounded Context Isolation

## Summary

Ephemeral cluster secrets are now scoped by `build_id` to prevent name collisions
when rebuilding clusters. This implements the bounded context philosophy where
each ephemeral build is fully isolated.

## Problem

Secrets Manager retains deleted secret names for the recovery window (default 30 days).
When tearing down and rebuilding ephemeral clusters, Terraform would fail with:

```
InvalidRequestException: You can't create this secret because a secret with
this name is already scheduled for deletion.
```

## Solution

Secret paths are now scoped by lifecycle:

| Lifecycle | Secret Path Pattern | Example |
|-----------|---------------------|---------|
| Persistent | `goldenpath/{env}/{component}` | `goldenpath/dev/rds/master` |
| Ephemeral | `goldenpath/{env}/builds/{build_id}/{component}` | `goldenpath/dev/builds/20-01-26-01/rds/master` |

Additionally:
- Ephemeral secrets use `recovery_window_in_days = 0` (immediate deletion)
- Persistent secrets use `recovery_window_in_days = 7` (safety buffer)

## Benefits

1. **No collisions** - Each ephemeral build gets unique secret paths
2. **Parallel builds** - Multiple ephemeral builds can run simultaneously
3. **Audit trail** - Secret names include build_id for traceability
4. **Clean teardown** - Secrets delete immediately, no 30-day hold

## Files Changed

| File | Change |
|------|--------|
| `envs/dev/main.tf` | Secret paths conditionally include `/builds/{build_id}/` for ephemeral |
| `modules/aws_rds/variables.tf` | Added `secret_recovery_window_in_days` variable |
| `modules/aws_rds/secrets.tf` | Applied recovery window to master and app secrets |

## Extends

This extends ADR-0006 (Platform Secrets Strategy) by adding lifecycle-aware
naming conventions. The base pattern `/goldenpath/<env>/<component>/<secret>`
remains for persistent clusters.
