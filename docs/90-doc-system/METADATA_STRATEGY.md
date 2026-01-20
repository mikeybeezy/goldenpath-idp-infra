---
id: METADATA_STRATEGY
title: Platform Metadata Strategy
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 11_SECRETS_CATALOG_POLICY
  - 35_RESOURCE_TAGGING
  - ADR-0050-platform-changelog-label-gate
  - ADR-0066-platform-dashboards-as-code
  - ADR-0140
  - ADR-0173-governance-doc-naming-migration
  - CL-0005-teardown-finalizer-default-on
  - CL-0101
  - METADATA_BACKFILL_RUNBOOK
  - METADATA_VALIDATION_GUIDE
  - RB-0018-metadata-backfill-script
  - RB-0019-relationship-extraction-script
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---
# Platform Metadata Strategy

## Goal

Transform the repository into a semantic knowledge graph to enable traceability, auditability, and automated governance.

## 1. Documentation Schema (YAML Frontmatter)

All markdown artifacts in `docs/` must include this header:

```yaml
---
# Core Identity

id: <Unique-ID>          # e.g., ADR-0066, CL-0005
title: <Title>
type: <Type>             # adr, changelog, policy, runbook
owner: <Team-Kebab-Case> # e.g., platform-team
status: <Status>         # draft, active, deprecated

# Governance & Risk (Due Diligence)

risk_profile:
  production_impact: <Low/Medium/High>
  security_risk: <None/Access/Secrets/Compliance>
  coupling_risk: <Low/High>

# Reliability

reliability:
  rollback_strategy: <git-revert/manual/automated>
  observability_tier: <gold/silver/bronze>

# Lifecycle

lifecycle:
  supported_until: <YYYY-MM-DD>
  breaking_change: <true/false>

# Linkage

relates_to:

- <Target-ID>          # e.g., ADR-0050

---

```

## 2. Infrastructure Schema (Standard Tags)

All Terraform modules and resources must include:

```hcl
tags = {
  # Identity & Grouping (Required)
  Owner       = "platform-team"
  Service     = "golden-path-idp"
  CostCenter  = "shared-platform"
  Category    = "compute" # compute, storage, network, database, observability

  # Governance Links
  DocsID      = "ADR-####"

}
```

## 3. Implementation Phases

1. **Standards:** Publish this schema.
2. **Backfill:** Update Template files (`ADR-TEMPLATE.md`) and existing critical docs.
3. **Scaffold:** Create new docs via `scripts/scaffold_doc.py` so headers match the schema by default.
4. **Local Auto-Fix:** Pre-commit runs `scripts/standardize_metadata.py` on changed docs to normalize headers.
5. **Enforcement:** Add `validate_metadata.py` to CI.

Coupled updates:
- If tag keys change, update `docs/10-governance/35_RESOURCE_TAGGING.md`
  and `docs/10-governance/11_SECRETS_CATALOG_POLICY.md` in the same PR.

## Doc Creation (Preferred)

Use the scaffold to generate new docs with compliant frontmatter:

```bash
# Standard doc
python3 scripts/scaffold_doc.py --path docs/90-doc-system/NEW_DOC.md --type documentation --owner platform-team

# ADR
python3 scripts/scaffold_doc.py --path docs/adrs/ADR-0140-platform-doc-metadata-autofix.md

# Changelog entry
python3 scripts/scaffold_doc.py --path docs/changelog/entries/CL-0101-doc-metadata-scaffold.md
```
