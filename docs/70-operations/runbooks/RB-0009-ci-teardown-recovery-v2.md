---
id: RB-0009-ci-teardown-recovery-v2
title: CI Teardown Recovery (v2)
type: runbook
risk_profile:
  production_impact: high
  security_risk: access
  coupling_risk: high
reliability:
  rollback_strategy: rerun-teardown
  observability_tier: gold
  maturity: 1
relates_to:
  - TEARDOWN_README
  - 07_TF_STATE_FORCE_UNLOCK
  - 08_MANAGED_LB_CLEANUP
  - CI_WORKFLOWS
category: runbooks
supported_until: 2028-01-01
version: 2.0
dependencies:
  - module:terraform
  - module:kubernetes
breaking_change: false
---

# CI Teardown Recovery (v2)

Use this when teardown hangs or state locks block cleanup. This sequence
recovers strictly via CI without requiring kube access.

## Preconditions

- `teardown_version=v2`
- `lifecycle=ephemeral`
- `build_id` available
- Cluster may already be gone or unreachable

## Workflow sequence

1) **CI Teardown**
   - Inputs: `env`, `region`, `build_id`, `lifecycle=ephemeral`,
     `teardown_version=v2`
   - If it hangs on LB/ENI cleanup, update the v2 script (see changelog) and
     re-run teardown.

2) **CI Force Unlock** (only if state lock blocks teardown)
   - Inputs: `env`, `region`, `build_id`, `lifecycle=ephemeral`,
     `lock_id=<uuid>`, `confirm_unlock=true`
   - Re-run **CI Teardown** or **teardown-resume** after unlock.

3) **CI Managed LB Cleanup** (when VPC delete is blocked by SGs)
   - Inputs: `env`, `region`, `build_id`, `lifecycle=ephemeral`,
     `dry_run=false`, `confirm_delete=true`,
     `delete_cluster_tagged_sgs=true`
   - Optional: `stack_tag=kong-system/dev-kong-kong-proxy` to narrow scope.

## Outcome

- Managed LB resources deleted
- VPC deletion unblocked
- Teardown completes via CI

## Recent successful run (reference)

- Build ID: `31-12-25-04`
- Duration: `11m39s` (~700s)
- Log: `logs/build-timings/teardown-dev-goldenpath-dev-eks-31-12-25-04-31-12-25-04-20260101T040157Z.log`
- Storage add-ons: EBS CSI + EFS CSI + snapshot controller enabled
