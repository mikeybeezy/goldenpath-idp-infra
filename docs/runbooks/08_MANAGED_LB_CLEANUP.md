# Managed LB Resource Cleanup (Runbook)

Use this when the EKS cluster is gone but VPC deletion fails due to
AWS Load Balancer Controller managed resources (LBs, ENIs, security groups).

## Inputs you need

- `env`
- `region`
- `cluster_name` (or `build_id` + `lifecycle=ephemeral` to resolve)
- Optional `stack_tag` (example: `kong-system/dev-kong-kong-proxy`)

## Steps

1) Run **CI Managed LB Cleanup** in dry-run to verify scope.

2) Re-run with `dry_run=false` and `confirm_delete=true`.

3) Retry teardown or orphan cleanup after the managed resources are removed.

## Notes

- This workflow only deletes resources tagged with `elbv2.k8s.aws/cluster`.
- Use `stack_tag` to narrow cleanup to a single service stack when needed.
- If deletions fail due to dependencies, re-run after LBs finish deleting.
