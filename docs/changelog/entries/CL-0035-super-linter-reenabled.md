---
id: CL-0035-super-linter-reenabled
title: 'Changelog: re-enable super-linter and require lint checks'
type: changelog
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
version: '1.0'
lifecycle: active
relates_to:
  - CL-0035
supported_until: 2027-01-04
breaking_change: false
---

# Changelog: re-enable super-linter and require lint checks

Date: 2026-01-03
Owner: platform

## Summary

- Re-enable the Markdown super-linter workflow for docs PRs.
- Document Yamllint and Super Linter as required status checks.

## References

- Workflow: .github/workflows/super-linter.yml
- Docs: docs/10-governance/04_PR_GUARDRAILS.md
- Docs: docs/80-onboarding/24_PR_GATES.md
