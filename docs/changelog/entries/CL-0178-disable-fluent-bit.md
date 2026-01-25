---
id: CL-0178
title: Disable Fluent Bit (Promtail Preferred)
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
  - 20_TOOLING_APPS_MATRIX
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-24
author: platform-team
breaking_change: false
---

## Summary

Disabled Fluent Bit log collector in favor of Promtail, which is native to Loki.

## Problem

Both Fluent Bit and Promtail were deployed, causing:
- **Redundant log collection** - Both tools ship logs to Loki
- **Wasted resources** - 6 Fluent Bit pods consuming CPU/memory unnecessarily
- **Failing health checks** - Fluent Bit pods showing readiness probe failures

```
Warning   Unhealthy   pod/dev-fluent-bit-*   Readiness probe failed: HTTP probe failed with statuscode: 500
```

## Decision

**Keep Promtail, disable Fluent Bit** because:

| Criteria | Promtail | Fluent Bit |
|----------|----------|------------|
| Native to Loki | ✅ Yes |  No |
| Status | ✅ Working |  Failing |
| Complexity | Simple | More complex |
| Use case | Loki-only | Multi-destination |

Since the platform uses Loki for log aggregation, Promtail is the better choice.

## Changes

Renamed ArgoCD app files to `.disabled` (preserves configuration for future use):

```
gitops/argocd/apps/dev/fluent-bit.yaml      → fluent-bit.yaml.disabled
gitops/argocd/apps/staging/fluent-bit.yaml  → fluent-bit.yaml.disabled
gitops/argocd/apps/prod/fluent-bit.yaml     → fluent-bit.yaml.disabled
gitops/argocd/apps/test/fluent-bit.yaml     → fluent-bit.yaml.disabled
```

## Resource Savings

Per environment (assuming 6-node cluster):

| Resource | Requests (saved) | Limits (saved) |
|----------|------------------|----------------|
| CPU | 300m (6 × 50m) | 1.2 cores (6 × 200m) |
| Memory | 384Mi (6 × 64Mi) | 768Mi (6 × 128Mi) |

## Re-enabling Fluent Bit

If needed in the future (e.g., shipping logs to multiple destinations):

```bash
# Rename back to .yaml
git mv gitops/argocd/apps/dev/fluent-bit.yaml.disabled \
       gitops/argocd/apps/dev/fluent-bit.yaml

# Commit and push
git add -A && git commit -m "feat: re-enable Fluent Bit" && git push
```

## Manual Cleanup (Existing Clusters)

For clusters where Fluent Bit is already deployed:

```bash
# Delete the ArgoCD application
kubectl delete application dev-fluent-bit -n argocd

# Or if ArgoCD app doesn't exist, delete resources directly
kubectl delete daemonset -n monitoring -l app.kubernetes.io/name=fluent-bit
```

## Files Changed

- `gitops/argocd/apps/dev/fluent-bit.yaml` → `.disabled`
- `gitops/argocd/apps/staging/fluent-bit.yaml` → `.disabled`
- `gitops/argocd/apps/prod/fluent-bit.yaml` → `.disabled`
- `gitops/argocd/apps/test/fluent-bit.yaml` → `.disabled`

## Impact

- Non-breaking change
- Reduces resource consumption
- Simplifies observability stack
- Logs continue to flow via Promtail
