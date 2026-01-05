---
id: 08_MANAGED_LB_CLEANUP
title: Managed LB Resource Cleanup (Runbook)
type: runbook
category: runbooks
version: 1.0
owner: platform-team
status: active
dependencies:
  - chart:aws-load-balancer-controller
risk_profile:
  production_impact: high
  security_risk: access
  coupling_risk: medium
reliability:
  rollback_strategy: not-applicable
  observability_tier: gold
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - TEARDOWN_README
  - 04_LB_FINALIZER_STUCK
  - 15_TEARDOWN_AND_CLEANUP
  - CI_WORKFLOWS
---

# Managed LB Resource Cleanup (Runbook)

Use this when the EKS cluster is gone but VPC deletion fails due to
AWS Load Balancer Controller managed resources (LBs, ENIs, security groups).

## Inputs you need

- `env`
- `region`
- `cluster_name` (or `build_id` + `lifecycle=ephemeral` to resolve)
- Optional `stack_tag` (example: `kong-system/dev-kong-kong-proxy`)
- Optional `delete_cluster_tagged_sgs` (true/false)

## Steps

1) Run **CI Managed LB Cleanup** in dry-run to verify scope.

2) Re-run with `dry_run=false` and `confirm_delete=true`.

3) Retry teardown or orphan cleanup after the managed resources are removed.

## Notes

- This workflow only deletes resources tagged with `elbv2.k8s.aws/cluster`.
- Use `stack_tag` to narrow cleanup to a single service stack when needed.
- If `delete_cluster_tagged_sgs=true`, the workflow also deletes any
  security group tagged with `elbv2.k8s.aws/cluster` (excluding `default`).
- If deletions fail due to dependencies, re-run after LBs finish deleting.
