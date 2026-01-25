<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0074-config-driven-metadata-governance
title: Transition to Config-Driven Metadata Governance
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
  coupling_risk: none
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - ADR-0118-config-driven-metadata-governance
  - CL-0074-config-driven-metadata-governance
  - CONFIG_DRIVEN_METADATA
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-06
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: 1.0
date: 2026-01-06
breaking_change: false
---

## CL-0074: Transition to Config-Driven Metadata Governance

## Summary

Decoupled metadata standardization and validation logic from hardcoded Python scripts, moving the source of truth to YAML schemas and enums.

## Changes

- **New Governance Framework**: Published [**`CONFIG_DRIVEN_METADATA.md`**](../../10-governance/CONFIG_DRIVEN_METADATA.md).
- **Core Engine Implementation**: Created [**`metadata_config.py`**](../../../scripts/lib/metadata_config.py) to unify schema loading.
- **Refactored Validators**: Updated index/schema validators to use config-driven logic.
- **Refactored Healer**: Updated `standardize_metadata.py` to use dynamic schema skeletons.

## Verification

- Verified validation gates still correctly flag missing required fields derived from schemas.
- Confirmed that adding a field to a schema YAML automatically propagates to the "Healer" script.
