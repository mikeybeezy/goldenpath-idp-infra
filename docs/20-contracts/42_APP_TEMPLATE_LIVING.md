---
id: 42_APP_TEMPLATE_LIVING
title: App Template Living Doc
type: contract
risk_profile:
  production_impact: medium
  security_risk: none
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
relates_to:
  - 02_PLATFORM_BOUNDARIES
  - ADR-0062-platform-app-template-contract
  - ADR-0078-platform-governed-repo-scaffolder
  - APPS_FAST-API-APP-TEMPLATE_README
  - CL-0011-app-template-contract
  - CL-0031-governed-repo-scaffolder
  - FAST-API-APP-TEMPLATE
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---
# App Template Living Doc

Doc contract:

- Purpose: Track the current app template structure and ownership boundaries.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/adrs/ADR-0062-platform-app-template-contract.md, docs/20-contracts/02_PLATFORM_BOUNDARIES.md, apps/fast-api-app-template/README.md

This is a living reference for the team-owned app template and its structure.
It is updated whenever the template changes.

## Current Structure (ASCII)

```
apps/fast-api-app-template/
├─ README.md
├─ deployment.yaml
├─ service.yaml
├─ servicemonitor.yaml
├─ ingress.yaml
├─ catalog-info.yaml
├─ serviceaccount.yaml
├─ rbac.yaml
├─ networkpolicy.yaml
├─ dashboards/
│  └─ configmap-dashboard.yaml
└─ kong/
   ├─ kong-auth-plugin.yaml
   ├─ kong-rate-limiting.yaml
   ├─ kong-consumer.yaml
   └─ kong-secret.yaml
```

## Ownership Boundaries

App-owned:

- deployment.yaml
- service.yaml
- servicemonitor.yaml
- dashboards/configmap-dashboard.yaml
- ingress.yaml values (host/path/service/ports)

Platform-owned:

- kong/*
- networkpolicy.yaml
- rbac.yaml (only when needed)

## Scaffolder contract (governance metadata)

Required inputs (Backstage + CI scaffolder):

- `owner_team` (GitHub team slug, e.g., checkout-team)
- `system` (Backstage system; optional)
- `lifecycle` (experimental, production, deprecated)
- `service_tier` (tier-1, tier-2, tier-3)
- `data_classification` (public, internal, confidential, restricted)

Catalog fields:

- `spec.owner` is set to `group:<owner_team>`
- `spec.lifecycle` and annotations under `platform.goldenpath.dev/*`

Workflow requirements:

- `REPO_SCOPED_GH_TOKEN` secret with repo creation permissions.

## Change Log (Living)

- 2025-12-31: Initial reference template added with placeholders and Kong +
  observability defaults.
