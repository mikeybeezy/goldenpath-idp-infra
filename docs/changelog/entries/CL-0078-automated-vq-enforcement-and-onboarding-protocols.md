---
id: CL-0078
title: 'CL-0078: Automated VQ Enforcement and Onboarding Protocols'
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
  - 13_COLLABORATION_GUIDE
  - 23_NEW_JOINERS
  - 25_DAY_ONE_CHECKLIST
  - 26_AI_AGENT_PROTOCOLS
  - ADR-0122
  - AGENT_FIRST_BOOT
  - CL-0078
  - VQ_PRINCIPLES
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: '2028-01-01'
---
# CL-0078: Automated VQ Enforcement and Onboarding Protocols

Date: 2026-01-07
Owner: platform-team
Scope: Governance & Onboarding
Related: ADR-0122

## Summary

Implemented automated enforcement of Value Quantification (VQ) for AI agents and formalized the "First-Boot" and "Pulse" recovery protocols for all contributors.

## Changes

### Added
- `docs/80-onboarding/AGENT_FIRST_BOOT.md`: Mandatory context anchor for AI agents.
- `docs/80-onboarding/metadata.yaml`: Established directory-level VQ inheritance for all onboarding docs.

### Changed
- `bin/governance`: Added `pulse` command for terminal-based mission re-centering.
- `scripts/pr_guardrails.py`: Added "Agent VQ Check" to auto-fail agent PRs lacking value classification.
- `docs/80-onboarding/23_NEW_JOINERS.md`: Added "Value Delivery" expectations.
- `docs/80-onboarding/25_DAY_ONE_CHECKLIST.md`: Integrated VQ principles into the fast-path checklist.
- `docs/80-onboarding/13_COLLABORATION_GUIDE.md`: Added "Value-Led Review" section.
- `docs/80-onboarding/26_AI_AGENT_PROTOCOLS.md`: Mandated VQ justification for all agent-proposed changes.

## Validation

- Verified `pr_guardrails.py` block/pass logic for agent-authored PRs.
- Verified `bin/governance pulse` output formatting.
- Verified metadata inheritance in `docs/80-onboarding/`.
- Repository remains in 100% Green state (543 assets).
