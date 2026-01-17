---
id: CL-0126
title: CI Governance Registry Fetch for Build ID Validation
type: changelog
status: released
owner: platform-team
domain: platform-core
applies_to:
  - infra-terraform-apply-dev.yml
  - infra-terraform-apply-staging.yml
  - infra-terraform-apply-prod.yml
  - infra-terraform-apply-test.yml
  - ci-bootstrap.yml
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
schema_version: 1
relates_to:
  - ADR-0148
  - ADR-0148-seamless-build-deployment-with-immutability
  - ADR-0155
  - ADR-0155-ci-governance-registry-fetch
supersedes: []
superseded_by: []
tags:
  - ci
  - governance
  - security
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.5
supported_until: '2028-01-14'
date: 2026-01-14
author: Michael Nouriel
description: Adds explicit governance-registry branch fetch to CI workflows to ensure
  build_id immutability validation cannot be bypassed due to shallow clones.
---
# CI Governance Registry Fetch for Build ID Validation

This release hardens the build_id immutability check by ensuring CI workflows always have access to the governance-registry branch before running terraform apply.

## Problem

The build_id immutability guard in `envs/dev/main.tf` checks whether a build_id has been previously used by querying a CSV file on the `governance-registry` branch. However, CI workflows use shallow clones that don't include this branch, causing the check to silently return "not found" and allow potentially duplicate build_ids to proceed.

**Before this fix:**
- CI shallow clone has no `governance-registry` branch
- `git show origin/governance-registry:...` fails silently
- Validation returns `exists=false` (fail-open)
- Duplicate build_id proceeds, risking state collision

## Solution

Add an explicit fetch step to all deployment workflows:

```yaml
- name: Fetch governance registry for build_id validation
  run: git fetch origin governance-registry:refs/remotes/origin/governance-registry
```

## Affected Workflows

| Workflow | File |
|----------|------|
| Apply - Infra Terraform Apply (dev) | `.github/workflows/infra-terraform-apply-dev.yml` |
| Apply - Infra Terraform Apply (staging) | `.github/workflows/infra-terraform-apply-staging.yml` |
| Apply - Infra Terraform Apply (prod) | `.github/workflows/infra-terraform-apply-prod.yml` |
| Apply - Infra Terraform Apply (test) | `.github/workflows/infra-terraform-apply-test.yml` |
| Bootstrap | `.github/workflows/ci-bootstrap.yml` |

## Impact

### CI Behavior

- Build_id validation now works correctly in all CI runs
- Duplicate build_ids will be blocked as intended
- ~1-2 second increase in workflow time (fetch step)

### Local Development

- No change to `make deploy` behavior
- Developers who haven't fetched the branch will see a clear error message
- Fix: `git fetch origin governance-registry`

## Verification

After deployment, verify the fix by:

1. Check workflow logs show the fetch step completing
2. Attempt to reuse a known build_id - should be blocked
3. Use a new build_id - should proceed normally

## Related

- [ADR-0155: CI Governance Registry Fetch](../adrs/ADR-0155-ci-governance-registry-fetch.md)
- [ADR-0148: Seamless Build Deployment](../adrs/ADR-0148-seamless-build-deployment-with-immutability.md)
