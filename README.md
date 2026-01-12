# Governance Registry

This branch is a **CI-owned observation context** that stores derived governance artifacts:
- Platform health reports
- Documentation indices
- Audit logs

## 🔒 Write Boundary

**CRITICAL**: This branch accepts commits **ONLY from CI/CD workflows**. 
- ✅ Automated writes via GitHub Actions
- ❌ Manual commits by humans (policy violation)

## 📁 Structure

```
governance-registry/
├── UNIFIED_DASHBOARD.md          # Cross-environment dashboard
└── environments/
    ├── development/
    │   ├── latest/                # Current state
    │   │   └── PLATFORM_HEALTH.md
    │   └── history/               # Audit trail
    │       └── <date>-<sha>/
    └── production/
        ├── latest/
        └── history/
```

## 🔗 Chain of Custody

Every artifact in this branch includes mandatory provenance metadata:
- `source.sha` - Git commit that generated the report
- `pipeline.run_id` - GitHub Actions run ID
- `generated_at` - UTC timestamp
- `integrity.derived_only` - Must be `true`

## 📖 Documentation

- **Architecture**: [ADR-0145: Governance Registry Mirror](https://github.com/mikeybeezy/goldenpath-idp-infra/blob/development/docs/adrs/ADR-0145-governance-registry-mirror.md)
- **Operations**: [RB-0028: Registry Operations](https://github.com/mikeybeezy/goldenpath-idp-infra/blob/development/docs/70-operations/runbooks/RB-0028-governance-registry-operations.md)
- **How it Works**: [Governance Registry Mirror](https://github.com/mikeybeezy/goldenpath-idp-infra/blob/development/how-it-works/GOVERNANCE_REGISTRY_MIRROR.md)

## 🛡️ Integrity

This branch is validated on every push by `govreg-validate.yml`. The validator ensures:
- Only allowed folder structure exists
- All artifacts contain required metadata headers
- No manual patches bypass the ledger contract

**Generated**: 2026-01-12T11:57:00Z  
**Source Repository**: [goldenpath-idp-infra](https://github.com/mikeybeezy/goldenpath-idp-infra)
