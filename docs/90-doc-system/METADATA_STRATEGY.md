---
id: METADATA_STRATEGY
title: Platform Metadata Strategy
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
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
  - ADR-0050
  - ADR-0066
  - CL-0005
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
status: active
version: '1.0'
dependencies: []
supported_until: 2028-01-01
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
3. **Enforcement:** Add `validate_metadata.py` to CI.
