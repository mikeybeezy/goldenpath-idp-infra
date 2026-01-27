---
id: CL-0134-backstage-catalog-governance-registry-sync
title: Backstage Catalog Synced to Governance Registry
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - backstage
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0159-backstage-catalog-registry-sync
  - CL-0129
  - CL-0134-backstage-catalog-governance-registry-sync
  - CL-0135-kong-ingress-for-tooling-apps
  - agent_session_summary
supersedes: []
superseded_by: []
tags:
  - backstage
  - catalog
  - governance-registry
inheritance: {}
supported_until: 2028-01-16
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 1.0
version: '1.0'
breaking_change: false
---

## CL-0134: Backstage Catalog Synced to Governance Registry

**Type**: Configuration
**Component**: Backstage / Catalog
**Date**: 2026-01-16
**Related**: ADR-0159, CL-0129

## Summary

Synced the `backstage-catalog/` directory to the `governance-registry` branch and updated all environment values files to reference the new location.

## Changes

### Catalog Location Migration

### Before

```yaml
catalogLocation: "https://raw.githubusercontent.com/mikeybeezy/goldenpath-idp-infra/main/backstage-helm/backstage-catalog/all.yaml"
```

### After

```yaml
catalogLocation: "https://raw.githubusercontent.com/mikeybeezy/goldenpath-idp-infra/governance-registry/backstage-helm/backstage-catalog/all.yaml"
```

### Files Updated

|File|Change|
|------|--------|
|`gitops/helm/backstage/values/dev.yaml`|Catalog URL updated|
|`gitops/helm/backstage/values/staging.yaml`|Catalog URL updated|
|`gitops/helm/backstage/values/prod.yaml`|Catalog URL updated|
|`backstage-helm/values-local.yaml`|Catalog URL updated (2 locations)|

### Governance Registry Sync

Pushed 351 catalog files to `governance-registry` branch including:

- APIs, components, domains, systems, resources
- ADRs and changelogs index
- ECR and RDS request templates
- Organization and group definitions

## Rationale

Per ADR-0159, the Backstage catalog should be served from a stable branch (`governance-registry`) rather than feature branches or `main`. This ensures:

1. **Stability**: Catalog doesn't break during feature development
2. **Separation of concerns**: Infrastructure changes don't affect catalog availability
3. **Predictability**: Known location for all environments

## Verification

```bash
# Verify catalog is accessible
curl -s "https://raw.githubusercontent.com/mikeybeezy/goldenpath-idp-infra/governance-registry/backstage-helm/backstage-catalog/all.yaml" | head -5

# Verify Backstage loads catalog
kubectl logs -n backstage -l app.kubernetes.io/name=backstage | grep -i catalog
```

## References

- ADR: `docs/adrs/ADR-0159-backstage-catalog-registry-sync.md`
- Original changelog: CL-0129

---

**Historical Note (2026-01-26):** References to `backstage-helm/` paths in this document are historical. Per CL-0196, the directory structure was consolidated:
- `backstage-helm/charts/backstage/` → `gitops/helm/backstage/chart/`
- `backstage-helm/backstage-catalog/` → `catalog/`
