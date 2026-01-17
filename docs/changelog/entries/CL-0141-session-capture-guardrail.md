---
id: CL-0141
title: Session Capture Append-Only Guardrail
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - .github/workflows/session-capture-guard.yml
  - session_capture/session_capture_template.md
  - session_summary/session_summary_template.md
  - docs/10-governance/07_AI_AGENT_GOVERNANCE.md
  - docs/80-onboarding/25_DAY_ONE_CHECKLIST.md
  - docs/80-onboarding/26_AI_AGENT_PROTOCOLS.md
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
schema_version: 1
relates_to:
  - 07_AI_AGENT_GOVERNANCE
  - 25_DAY_ONE_CHECKLIST
  - 26_AI_AGENT_PROTOCOLS
  - ADR-0167
  - CL-0141
  - SESSION_CAPTURE_2026_01_17_02
  - agent_session_summary
  - session_capture_template
  - session_summary_template
supersedes: []
superseded_by: []
tags:
  - governance
  - documentation
  - guardrail
  - ci
inheritance: {}
value_quantification:
  vq_class: LV/HQ
  impact_tier: low
  potential_savings_hours: 4.0
supported_until: 2028-01-17
date: 2026-01-17
author: platform-team
---
# Session Capture Append-Only Guardrail

## Summary

Added a session capture template and a CI guardrail that enforces append-only
updates with timestamped headers. Updated governance and onboarding docs to
standardize adoption.

## Impact

- Documentation process now has a dedicated append-only enforcement for
  `session_capture/**`.
- PRs editing session capture files will be blocked if they edit existing
  content or omit a timestamped update header.

## Files

- `.github/workflows/session-capture-guard.yml`
- `session_capture/session_capture_template.md`
- `session_summary/session_summary_template.md`
- `docs/10-governance/07_AI_AGENT_GOVERNANCE.md`
- `docs/80-onboarding/25_DAY_ONE_CHECKLIST.md`
- `docs/80-onboarding/26_AI_AGENT_PROTOCOLS.md`
