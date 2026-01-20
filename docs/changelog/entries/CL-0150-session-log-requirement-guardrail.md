---
id: CL-0150
title: Session Log Requirement Guardrail
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - .github/workflows/session-log-required.yml
  - docs/10-governance/PR_GUARDRAILS_INDEX.md
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
schema_version: 1
relates_to:
  - 07_AI_AGENT_GOVERNANCE
  - 26_AI_AGENT_PROTOCOLS
  - PR_GUARDRAILS_INDEX
  - session_capture_template
  - session_summary_template
supersedes: []
superseded_by: []
tags:
  - governance
  - guardrail
  - ci
inheritance: {}
value_quantification:
  vq_class: 🔵 MV/HQ
  impact_tier: low
  potential_savings_hours: 2.0
supported_until: 2028-01-20
date: 2026-01-20
author: platform-team
---

# Session Log Requirement Guardrail

## Summary

Added a PR guardrail that requires both a session capture update and a session
summary update whenever critical platform paths change.

## Impact

- PRs touching workflows, gitops, bootstrap, modules, scripts, governance docs,
  ADRs, or runbooks must include:
  - a session capture update in `session_capture/**` (append-only)
  - a session summary update in `session_summary/agent_session_summary.md`

## Files

- `.github/workflows/session-log-required.yml`
- `docs/10-governance/PR_GUARDRAILS_INDEX.md`
