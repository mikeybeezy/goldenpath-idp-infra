<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0164
title: ArgoCD Plugin Integration for Backstage
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - goldenpath-idp-backstage/packages/app/src/components/catalog/EntityPage.tsx
  - goldenpath-idp-backstage/packages/backend/src/index.ts
  - goldenpath-idp-backstage/app-config.yaml
  - goldenpath-idp-backstage/app-config.production.yaml
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
schema_version: 1
relates_to:
  - CL-0163-backstage-ecr-branding-session-memory
  - ADR-0176-session-memory-management
supersedes: []
superseded_by: []
tags:
  - backstage
  - argocd
  - plugin
  - gitops
inheritance: {}
supported_until: 2028-01-22
value_quantification:
  vq_class: HV/LQ
  impact_tier: high
  potential_savings_hours: 20.0
date: 2026-01-22
author: platform-team
---

# ArgoCD Plugin Integration for Backstage

## Summary

Integrated the Roadie ArgoCD plugin into Backstage to provide deployment visibility directly within the developer portal. Developers can now view ArgoCD sync status, health status, and deployment history for their services without leaving Backstage.

## Decision: Why Roadie Over Red Hat Plugin

We evaluated three ArgoCD plugins for Backstage:

| Plugin | Package | Consideration |
|--------|---------|---------------|
| **Roadie** | `@roadiehq/backstage-plugin-argo-cd` | Selected |
| Red Hat | `@backstage-community/plugin-redhat-argocd` | Rejected |
| Janus IDP | `@janus-idp/backstage-plugin-argocd` | Rejected |

### Rationale for Roadie

1. **Standalone Architecture**: Roadie plugin works independently without requiring the Kubernetes plugin to be fully configured first. Red Hat's plugin has a hard dependency on K8s plugin setup.

2. **Maturity**: Roadie plugin has 3+ years of production use and broader community adoption (~15k weekly npm downloads vs ~2k for Red Hat).

3. **Simpler Setup**: Roadie requires only app-config.yaml changes and basic frontend wiring. Red Hat requires additional Kubernetes plugin prerequisites.

4. **Documentation**: More community examples and troubleshooting resources available for Roadie.

5. **Future Flexibility**: If we later need tighter K8s integration, we can evaluate switching to Red Hat's plugin. Starting simpler reduces initial complexity.

## What Changed

### Frontend (EntityPage.tsx)

- Added `EntityArgoCDOverviewCard` to service/website overview pages
- Added ArgoCD tab with `EntityArgoCDHistoryCard` for deployment history
- Components conditionally render based on `isArgocdAvailable`

### Backend (index.ts)

- Added `@roadiehq/backstage-plugin-argo-cd-backend` plugin registration

### Configuration (app-config.yaml)

- Added `argocd` configuration block with:
  - Instance configuration (name, URL)
  - Support for token-based authentication
  - App locator method using config

## Entity Annotation Required

To enable ArgoCD for an entity, add this annotation to `catalog-info.yaml`:

```yaml
metadata:
  annotations:
    argocd/app-name: my-argocd-app
    # Or for multiple apps:
    # argocd/app-selector: app.kubernetes.io/instance=my-app
```

## Files Added/Modified

### goldenpath-idp-backstage

**Modified:**

- `packages/app/src/components/catalog/EntityPage.tsx`
- `packages/backend/src/index.ts`
- `packages/app/package.json`
- `packages/backend/package.json`
- `app-config.yaml`
- `app-config.production.yaml`

**Dependencies Added:**

- `@roadiehq/backstage-plugin-argo-cd: ^3.0.0`
- `@roadiehq/backstage-plugin-argo-cd-backend: ^4.6.0`

## Environment Variables Required

For production deployment, set:

```bash
ARGOCD_URL=https://argocd.goldenpathidp.io
ARGOCD_AUTH_TOKEN=<argocd-api-token>
```

## Value Delivered

- **Developer Experience**: View deployment status without context-switching to ArgoCD UI
- **Observability**: Quick health/sync status on entity overview cards
- **Audit Trail**: Deployment history visible per service
- **GitOps Visibility**: Connects code changes to deployment outcomes

## Verification

```bash
# Verify plugin installed
grep -r "roadiehq.*argo-cd" packages/*/package.json

# Verify frontend integration
grep -r "ArgoCD" packages/app/src/components/catalog/EntityPage.tsx

# Verify backend registration
grep -r "argo-cd-backend" packages/backend/src/index.ts
```

## Related Documentation

- [Roadie ArgoCD Plugin](https://roadie.io/backstage/plugins/argo-cd/)
- [Backstage ArgoCD Integration](https://backstage.io/docs/features/software-catalog/well-known-annotations)
