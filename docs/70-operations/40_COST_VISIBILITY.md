---
id: 40_COST_VISIBILITY
title: Cost Visibility (CI + Infracost)
type: policy
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 06_COST_GOVERNANCE
  - 70_OPERATIONS_README
  - ADR-0076-platform-infracost-ci-visibility
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
category: compliance
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# Cost Visibility (CI + Infracost)

Doc contract:

- Purpose: Describe the current cost visibility implementation and how to operate it.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/10-governance/06_COST_GOVERNANCE.md, docs/adrs/ADR-0076-platform-infracost-ci-visibility.md, .github/workflows/pr-terraform-plan.yml

## Summary

We use Infracost in CI to surface Terraform cost impact on PRs. The signal is
advisory and does not block merges.

## Current implementation

- Workflow: `.github/workflows/pr-terraform-plan.yml`
- Trigger: Terraform PRs (`*.tf`, `*.tfvars`)
- Input: `plan.json` generated from the PR Terraform plan
- Output: Infracost PR comment with cost breakdown

## Requirements

- GitHub secret: `INFRACOST_API_KEY`
- Infracost is skipped if the API key is not set.

## Operator notes

- Infracost comments are informational and should not be treated as pass/fail.
- For large deltas, reviewers should request clarification or follow-up.

## Known limitations (V1)

- No baseline diff vs `main` yet.
- No thresholds or budgets enforced.

## Future enhancements

- Add baseline diff (main vs PR) to show deltas.
- Optional budget thresholds for high-risk changes.
- Backstage scorecard integration for cost visibility.
