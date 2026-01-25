<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: DOCS_PRDS_README
title: Product Requirements Docs (PRDs)
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
  - 00_INDEX
  - PRD-0000-template
  - PRD-0001-rds-user-db-provisioning
  - PRD-0002-route53-externaldns
  - PRD-0003-backstage-plugin-scaffold
  - PRD-0004-backstage-repo-structure-alignment
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# Product Requirements Docs (PRDs)

Purpose: capture product and feature requirements (the "what" and "why") before
implementation. PRDs describe scope, success criteria, and constraints. ADRs
capture decisions, tradeoffs, and the chosen approach.

Index: `docs/20-contracts/prds/00_INDEX.md`
Template: `docs/20-contracts/prds/PRD-0000-template.md`

## Rules

- Keep PRDs short and outcome-focused.
- Use the numbering sequence `PRD-0001`, `PRD-0002`, etc.
- Filenames and IDs must match the full filename base (e.g., `PRD-0001-<slug>`).
- Link to related ADRs and changelog entries when they exist.
