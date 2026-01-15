---
id: ADR-0159-backstage-catalog-registry-sync
title: 'ADR-0159: Backstage Catalog Sync to Governance Registry'
type: adr
status: accepted
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0145
  - ADR-0158
supersedes: []
superseded_by: []
tags:
  - backstage
  - governance-registry
  - catalog
  - self-service
inheritance: {}
value_quantification:
  vq_class: 🟢 HV/HQ
  impact_tier: medium
  potential_savings_hours: 20.0
supported_until: 2028-01-15
version: 1.0
breaking_change: false
---

# ADR-0159: Backstage Catalog Sync to Governance Registry

- **Status:** Accepted
- **Date:** 2026-01-15
- **Owners:** Platform Team
- **Domain:** Platform Core
- **Decision type:** Architecture / Developer Experience
- **Related:** ADR-0145 (Governance Registry Mirror), ADR-0158 (Standalone RDS)

---

## Context

The Backstage Software Catalog provides self-service templates for developers to provision resources (ECR registries, RDS databases, etc.). Previously, the catalog URL in Backstage configuration pointed to the `main` branch:

```yaml
catalogLocation: "https://raw.githubusercontent.com/mikeybeezy/goldenpath-idp-infra/main/backstage-helm/backstage-catalog/all.yaml"
```

This creates several operational challenges:

1. **Environment drift** - Each environment (dev/staging/prod) could point to different branches
2. **Config sprawl** - Catalog URL changes require updating Backstage values per environment
3. **No review gate** - Changes to `main` immediately affect all Backstage instances
4. **Inconsistent reference** - Development work on catalog happens on feature branches

The platform already uses a `governance-registry` branch (ADR-0145) as a CI-owned stable reference point for derived artifacts. Extending this pattern to include the Backstage catalog provides a consistent, environment-agnostic reference.

---

## Decision

**Sync the Backstage catalog to the `governance-registry` branch** and update all Backstage instances to reference this stable location.

### Implementation

1. **Extend `governance-registry-writer.yml`** to copy `backstage-helm/backstage-catalog/*` to `backstage-catalog/` on the registry branch
2. **Update `govreg.schema.yaml`** to allow `backstage-catalog/` as a valid top-level directory
3. **Update Backstage values.yaml** to reference the registry branch URL

### New Catalog URL

```yaml
catalogLocation: "https://raw.githubusercontent.com/mikeybeezy/goldenpath-idp-infra/governance-registry/backstage-catalog/all.yaml"
```

### Sync Flow

```text
development/main branch          governance-registry branch
        │                                    │
        │  push to dev/main                  │
        ▼                                    │
┌──────────────────────┐                     │
│ governance-registry- │                     │
│ writer.yml           │ ────────────────────┤
└──────────────────────┘                     │
        │                                    ▼
        │                     ┌──────────────────────────┐
        │                     │ backstage-catalog/       │
        │                     │ ├── all.yaml             │
        │                     │ ├── templates/           │
        │                     │ │   ├── ecr-request.yaml │
        │                     │ │   └── rds-request.yaml │
        │                     │ └── ...                  │
        │                     └──────────────────────────┘
        │                                    │
        │                                    ▼
        │                     ┌──────────────────────────┐
        │                     │ All Backstage instances  │
        │                     │ (dev, staging, prod)     │
        │                     └──────────────────────────┘
```

---

## Consequences

### Positive

| Benefit | Description |
|---------|-------------|
| **Single URL** | All environments reference same stable catalog location |
| **Review gate** | Catalog changes must merge to dev/main before reaching registry |
| **No env config** | Eliminate per-environment Backstage configuration updates |
| **Consistency** | Follows established governance-registry pattern (ADR-0145) |
| **Auditability** | Catalog syncs are tracked via CI commit history |

### Negative

| Risk | Mitigation |
|------|------------|
| **Sync delay** | Catalog changes have ~1-2 min delay before available (acceptable) |
| **Branch dependency** | If registry branch is broken, catalog unavailable (same as any branch) |

### Neutral

- Catalog is synced on every push to `development` or `main`
- No frontmatter injection for catalog files (not governance artifacts)
- Registry validation allows `backstage-catalog/` directory

---

## Alternatives Considered

### 1. Point to `main` branch directly

- **Rejected**: Couples development branch to production Backstage
- No review gate for catalog changes

### 2. Create dedicated `backstage-catalog` branch

- **Rejected**: Adds branch sprawl
- Governance-registry already provides stable reference pattern

### 3. Per-environment catalog URLs

- **Rejected**: Configuration drift
- Requires updating each environment's values.yaml

---

## Implementation

### Files Modified

| File | Change |
|------|--------|
| `.github/workflows/governance-registry-writer.yml` | Add catalog sync step |
| `backstage-helm/charts/backstage/values.yaml` | Update catalogLocation URL |
| `schemas/governance/govreg.schema.yaml` | Allow `backstage-catalog/` directory |

### Validation

```bash
# Verify catalog synced to registry
curl -s https://raw.githubusercontent.com/mikeybeezy/goldenpath-idp-infra/governance-registry/backstage-catalog/all.yaml

# Check Backstage can fetch templates
kubectl logs -n backstage deploy/backstage | grep -i catalog
```

---

## Related Documentation

- [ADR-0145: Governance Registry Mirror](./ADR-0145-governance-registry-mirror.md)
- [RDS Request Flow](../85-how-it-works/self-service/RDS_REQUEST_FLOW.md)
- [ECR Request Flow](../85-how-it-works/self-service/ECR_REQUEST_FLOW.md)
