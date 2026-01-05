---
id: CL-0033-github-agent-roles
title: 'Changelog: GitHub agent roles governance'
type: changelog
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2027-01-04
  breaking_change: false
relates_to:
  - ADR-0080
  - CL-0033
---

# Changelog: GitHub agent roles governance

Date: 2026-01-03
Owner: platform

## Summary

- Add governance guidance for GitHub App roles for AI/automation access.
- Add ADR documenting the GitHub App approach.
- Add a roadmap item to explore and validate agent roles.

## References

- ADR: docs/adrs/ADR-0080-platform-github-agent-roles.md
- Docs: docs/10-governance/08_GITHUB_AGENT_ROLES.md
