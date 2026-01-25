<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0077-value-quantification-framework
title: Value Quantification (VQ) Infrastructure
type: changelog
status: accepted
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
schema_version: 1
relates_to:
  - ADR-0121-value-quantification-framework
  - CL-0077-value-quantification-framework
  - VQ_TAGGING_GUIDE
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
date: 2026-01-07
---

# CL-0077: Value Quantification (VQ) Infrastructure

## Description
This change introduces the core infrastructure for **Value Quantification (VQ)** within the Golden Path IDP. It enables the platform to measure and report the financial and productivity impact of automation, governance, and architectural improvements.

## Changes
- **Schema Extension**: Updated `documentation.schema.yaml` to include the `value_quantification` object with `impact_tier` and `potential_savings_hours`.
- **Healer Update**: Modified `metadata_config.py` to ensure the VQ object is initialized in all new and auto-remediated metadata sidecars.
- **Strategic Documentation**:
  - Published [**`VQ_PRINCIPLES.md`**](../product/VQ_PRINCIPLES.md) (Philosophical foundation).
  - Published [**`VQ_TAGGING_GUIDE.md`**](../product/VQ_TAGGING_GUIDE.md) (SOP for developers).
- **Core Tagging**: Applied initial VQ tags to the main automation script library in `scripts/metadata.yaml`.

## Impact
- **Developer Experience**: Governance is now ROI-based, prioritizing "De-Friction" for high-impact workflows.
- **Reporting**: Enables the generation of automated ROI reports for stakeholders.
- **Compliance**: Maintains 100% "Born Governed" status for all VQ-related metadata.

## References
- [ADR-0121](../adrs/ADR-0121-value-quantification-framework.md)
