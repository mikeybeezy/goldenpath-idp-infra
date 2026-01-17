---
id: CL-0068-adr-index-automation
title: 'CL-0068: Automated ADR Index Generation'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
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
  - 01_adr_index
  - ADR-0112
  - CL-0068
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---
# CL-0068: Automated ADR Index Generation

## Summary
Introduced an automated system to generate and maintain the `docs/adrs/01_adr_index.md`. High-level "Gold Standard" metadata is now extracted directly from ADR files, ensuring zero drift between physical records and the index.

## Changes
- **New Script**: `scripts/generate_adr_index.py` for schema-driven index generation.
- **Workflow Integration**: Integrated with `ci-index-auto-heal.yml` for real-time drift detection and auto-remediation.
- **Index Markers**: Added injection markers to `01_adr_index.md` for safe automated updates.
- **ADR-0112**: Formalized the architectural decision to automate the index as Iteration 1 of the Knowledge Graph evolution.

## Verification Results
- **Drift Detection**: Verified that CI blocks and auto-heals when ADR metadata is modified without an index update.
- **Schema Parity**: Verified 1:1 mapping between ADR frontmatter and index table entries.
