---
id: CL-0036
title: 'Changelog: repo-wide linting for knowledge graph hygiene'
type: changelog
owner: platform-team
status: active
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
- ADR-0081
- CL-0036
------

# Changelog: repo-wide linting for knowledge graph hygiene

Date: 2026-01-03
Owner: platform

## Summary

- Run Super Linter (Markdown) on all PRs and main pushes.
- Run Yamllint repo-wide for `.yml` and `.yaml` files.
- Add ignore list for generated and vendor directories.

## References

- Workflow: .github/workflows/super-linter.yml
- Workflow: .github/workflows/yamllint.yml
- Config: .yamllint
- ADR: docs/adrs/ADR-0081-platform-repo-wide-linting.md
- Docs: docs/10-governance/04_PR_GUARDRAILS.md
