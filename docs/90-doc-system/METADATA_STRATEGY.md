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
3. **Enforcement:** Add `validate-metadata.py` to CI.
