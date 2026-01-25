<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0080
title: 'CL-0080: Documentation & Visibility Backfill'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to:
  - ADR-0124
  - CL-0080
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
---

# CL-0080: Documentation & Visibility Backfill

Date: 2026-01-07
Owner: platform-team
Scope: Documentation
Related: ADR-0124

## Summary

This entry backfills the governance record for the Documentation & Visibility suite, which ensures doc freshness, formatting, and relational accuracy.

## Changes

### Added
- `scripts/format_docs.py`: Whitespace and layout normalization.
- `scripts/check_doc_freshness.py`: Stale doc identification.
- `scripts/check_doc_index_contract.py`: Index policy enforcement.
- `scripts/extract_relationships.py`: Knowledge graph population.
- `scripts/generate_governance_vocab.py`: Vocabulary documentation.
- `scripts/sync_backstage_entities.py`: Backstage catalog synchronization.

## Validation

- Verified via `bin/governance audit` and Knowledge Graph consistency checks.
