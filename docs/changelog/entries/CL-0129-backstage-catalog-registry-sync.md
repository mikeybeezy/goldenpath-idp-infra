<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0129
title: Backstage Catalog Sync to Governance Registry
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - governance-registry-writer.yml
  - backstage-helm/charts/backstage/values.yaml
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
schema_version: 1
relates_to:
  - ADR-0145
  - ADR-0159-backstage-catalog-registry-sync
  - CL-0129
  - CL-0134-backstage-catalog-governance-registry-sync
supersedes: []
superseded_by: []
tags:
  - backstage
  - governance-registry
  - catalog
  - self-service
inheritance: {}
supported_until: 2028-01-15
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: medium
  potential_savings_hours: 20.0
date: 2026-01-15
author: platform-team
breaking_change: false
---

## Summary

- Backstage catalog now synced to `governance-registry` branch for stable access
- All environments reference single catalog URL (no per-env config)
- Catalog changes flow through PR review before reaching registry

## Impact

- **Platform team**: Simplified catalog management, no per-environment URL updates
- **Developers**: No change - Backstage templates work as before
- **Governance**: Catalog changes are tracked via CI commit history

## Changes

### Added

- Catalog sync step in `governance-registry-writer.yml`
- `backstage-catalog/` directory allowlist in `govreg.schema.yaml`

### Changed

- Backstage `catalogLocation` URL: `main` → `governance-registry` branch
  - Old: `https://raw.githubusercontent.com/.../main/backstage-helm/backstage-catalog/all.yaml`
  - New: `https://raw.githubusercontent.com/.../governance-registry/backstage-catalog/all.yaml`

### Documented

- [ADR-0159: Backstage Catalog Sync to Governance Registry](../../adrs/ADR-0159-backstage-catalog-registry-sync.md)

## Rollback / Recovery

```bash
# Revert Backstage values.yaml to point back to main branch
git checkout HEAD~1 -- backstage-helm/charts/backstage/values.yaml
```

## Validation

```bash
# Verify catalog accessible on registry branch
curl -I https://raw.githubusercontent.com/mikeybeezy/goldenpath-idp-infra/governance-registry/backstage-catalog/all.yaml

# Check templates listed
curl -s https://raw.githubusercontent.com/mikeybeezy/goldenpath-idp-infra/governance-registry/backstage-catalog/all.yaml | grep templates
```
