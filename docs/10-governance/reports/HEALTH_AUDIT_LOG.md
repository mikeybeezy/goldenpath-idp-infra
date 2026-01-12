---
id: HEALTH_AUDIT_LOG_REDIRECT
title: Platform Health Audit Log (Migrated)
type: redirect
status: deprecated
---

# ⚠️ This File Has Been Migrated

The **Platform Health Audit Log** has been migrated to the **Governance Registry** as part of ADR-0145.

## New Locations:

- **Latest Report:** [governance-registry/environments/development/latest/PLATFORM_HEALTH.md](https://github.com/mikeybeezy/goldenpath-idp-infra/blob/governance-registry/environments/development/latest/PLATFORM_HEALTH.md)
- **Historical Snapshots:** [governance-registry/environments/development/history/](https://github.com/mikeybeezy/goldenpath-idp-infra/tree/governance-registry/environments/development/history)

## Why This Change?

Per **ADR-0145: Governance Registry Mirror Pattern**, all machine-generated observation artifacts now live in the dedicated `governance-registry` branch to:

1. **Eliminate Commit Conflicts** - No more "fetch first" errors on active PRs
2. **Preserve Audit Trail** - Every historical snapshot is preserved with its source SHA
3. **Maintain Reproducibility** - Any commit can regenerate its exact report state

## Related Documentation:

- [ADR-0145: Governance Registry Mirror](/docs/adrs/ADR-0145-governance-registry-mirror.md)
- [RB-0028: Registry Operations](/docs/70-operations/runbooks/RB-0028-governance-registry-operations.md)
- [Migration Guide](/docs/10-governance/GOVERNANCE_REGISTRY_MIGRATION.md)

---

**Last Updated:** 2026-01-12  
**Migration Date:** 2026-01-12
