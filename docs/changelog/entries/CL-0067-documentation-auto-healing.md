---
id: CL-0067-documentation-auto-healing
title: 'CL-0067: Automated Documentation Auto-Healing'
type: documentation
category: changelog
version: 1.0
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-04
  breaking_change: false
relates_to:
  - ADR-0111
---

# CL-0067: Automated Documentation Auto-Healing

## Summary

Implemented a "Closed-Loop" documentation auto-healing system that automatically eliminates drift between physical repository files (scripts, workflows) and their respective indices.

## New Capabilities

1.  **Index Validation Mode**: Added `--validate` flag to indexing scripts to allow CI to detect drift without writing.
2.  **Auto-Heal Workflow**: Introduced `.github/workflows/ci-index-auto-heal.yml` which automatically commits documentation updates back to PR branches.

## Related ADRs

- [ADR-0111: Automated Documentation Auto-Healing](../adrs/ADR-0111-platform-documentation-auto-healing.md)

## Verification Results

- Verified that adding a script triggers an automated documentation commit.
- Verified that deleting a script triggers an automated cleanup commit.
- Confirmed fast-fail in validation mode.
