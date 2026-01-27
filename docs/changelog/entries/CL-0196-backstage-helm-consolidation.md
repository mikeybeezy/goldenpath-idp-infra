---
id: CL-0196-backstage-helm-consolidation
title: 'CL-0196: Backstage Helm Chart Consolidation'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: none
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
schema_version: 1
relates_to:
  - ADR-0066-platform-dashboards-as-code
  - APPS_DEV_BACKSTAGE
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-01
version: '1.0'
breaking_change: true
---

# CL-0196: Backstage Helm Chart Consolidation

Date: 2026-01-26
Author: Claude Opus 4.5

## Summary

Consolidates the scattered Backstage deployment artifacts into a clean structure.
Eliminates the confusing `backstage-helm/` directory which mixed chart templates,
catalog entities, and legacy local development files.

## Breaking Changes

- ArgoCD application `dev-backstage` path updated from `backstage-helm/charts/backstage`
  to `gitops/helm/backstage/chart`
- Catalog entities moved from `backstage-helm/backstage-catalog/` to `catalog/`
- References to `backstage-helm/` paths need updating in documentation and scripts

## Changes

### Directory Structure (Before)

```
backstage-helm/
  ├── charts/backstage/       # Helm chart (in use)
  ├── backstage-catalog/      # Catalog entities (in use)
  ├── local-deploy/           # Legacy
  ├── values-local.yaml       # Legacy
  ├── values-local.secrets.yaml # Legacy
  └── ...
gitops/helm/backstage/
  └── values/                 # Values only
```

### Directory Structure (After)

```
gitops/helm/backstage/
  ├── chart/                  # Helm chart templates
  │   ├── templates/
  │   ├── Chart.yaml
  │   └── values.yaml
  └── values/                 # Environment-specific values
      ├── dev.yaml
      ├── staging.yaml
      └── prod.yaml
catalog/                      # Backstage software catalog
  ├── all.yaml
  ├── apis/
  ├── components/
  ├── domains/
  └── ...
```

### Files Removed

- `backstage-helm/local-deploy/` - replaced by ArgoCD GitOps
- `backstage-helm/values-local.yaml` - replaced by `gitops/helm/backstage/values/`
- `backstage-helm/values-local.secrets.yaml` - replaced by ExternalSecrets
- `backstage-helm/img/` - unused documentation images
- `backstage-helm/reload-script.txt` - legacy dev notes
- `backstage-helm/.github/` - legacy workflows
- `backstage-helm/README.md` - outdated
- `backstage-helm/LICENSE` - duplicate
- `backstage-helm/BACKSTAGE_CATALOG_GOVERNANCE.md` - moved to catalog/
- `backstage-helm/CATALOG_TROUBLESHOOTING.md` - moved to catalog/
- `backstage-helm/PLUGIN_ENABLEMENT_MATRIX.md` - moved to docs/

## Required Forward Fixes

1. Update `governance-registry` branch catalog sync workflows
2. Update any documentation referencing old paths
3. Verify ArgoCD sync after deployment

## Verification

```bash
# After ArgoCD sync
kubectl get deployment -n backstage
argocd app get dev-backstage
```

## Rationale

- **Single source of truth**: Chart and values in same directory tree
- **Clear separation**: Helm deployment vs catalog entities
- **Reduced confusion**: No more legacy files mixed with active code
- **GitOps alignment**: All deployment artifacts under `gitops/`
