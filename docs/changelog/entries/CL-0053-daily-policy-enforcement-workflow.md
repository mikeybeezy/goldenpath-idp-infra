---
id: CL-0053-daily-policy-enforcement-workflow
title: 'CL-0053: Daily Policy Enforcement Workflow'
type: changelog
status: planned
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0092-ecr-registry-product-strategy
  - ADR-0093-automated-policy-enforcement
  - CL-0053-daily-policy-enforcement-workflow
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2027-01-05
version: '1.0'
breaking_change: false
---

# CL-0053: Daily Policy Enforcement Workflow

**Date:** 2026-01-05
**Type:** Feature
**Category:** Governance
**Status:** Planned

## Summary

Added GitHub Action workflow for automated daily policy compliance checks against ECR registries.

## Changes

### New Files
- `.github/workflows/policy-enforcement.yml` - Daily compliance check workflow
- `.github/workflows/README.md` - Workflow index documentation

### Workflow Details

**Trigger:** Daily at 09:00 UTC + manual dispatch

**Process:**
1. Load policies from `docs/10-governance/policies/*.yaml`
2. Query all ECR registries via AWS API
3. Check each registry against policy rules:
   - POL-ECR-001-R03: Required metadata present
   - POL-ECR-002-R01: Image scanning enabled
   - POL-ECR-003-R01: Lifecycle policy configured
   - POL-ECR-002-R04: CVEs remediated within SLA
4. Generate compliance report (JSON)
5. Create GitHub issues for violations
6. Send Slack alerts to #platform-team

**Outputs:**
- Compliance report artifact (90-day retention)
- GitHub issues for violations
- Slack notifications

## Impact

### Platform Team
- Automated daily compliance monitoring
- Proactive violation detection
- Reduced manual audit effort

### Application Teams
- Visibility into policy violations
- Clear remediation guidance via GitHub issues

## Implementation Status

- ✅ Workflow file created
-  Policy loading script (pending)
-  Compliance check script (pending)
-  Report generation script (pending)
-  Slack webhook integration (pending)

## Next Steps

1. Implement policy loading script (`scripts/policy-enforcement/check-policy-compliance.py`)
2. Test workflow with manual trigger
3. Validate compliance report format
4. Configure Slack webhook
5. Enable daily schedule

## Testing

- [ ] Manual workflow trigger works
- [ ] Policy YAML files load correctly
- [ ] ECR API queries succeed
- [ ] Compliance report generates
- [ ] GitHub issues created for violations
- [ ] Slack notifications sent

## Related
- [ADR-0093: Automated Policy Enforcement](../adrs/ADR-0093-automated-policy-enforcement.md)
- [ADR-0092: ECR Registry Product Strategy](../adrs/ADR-0092-ecr-registry-product-strategy.md)
- [Policy Governance README](../policies/README.md)
