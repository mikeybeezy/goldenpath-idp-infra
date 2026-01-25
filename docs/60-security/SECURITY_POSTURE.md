<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: SECURITY_POSTURE
title: Security Posture
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
  - 06_IDENTITY_AND_ACCESS
  - ADR-0024-platform-security-floor-v1
category: security
supported_until: 2028-01-01
version: 1.0
breaking_change: false
---
