<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: 39_GOLDEN_PATH_VALIDATION
title: Golden Path Validation (Living)
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 21_CI_ENVIRONMENT_CONTRACT
  - 34_PLATFORM_SUCCESS_CHECKLIST
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# Golden Path Validation (Living)

Doc contract:

- Purpose: Validate the end-to-end golden path flow.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md, docs/00-foundations/34_PLATFORM_SUCCESS_CHECKLIST.md

This checklist validates the end-to-end "golden path" for infra build, bootstrap,
and teardown using the PR-driven flow.

Run it after workflow changes or before a release cut.

---

Authoritative flow diagram: `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`. This
checklist follows that flow and does not redefine it.

## Preconditions

- Target environment: `dev`.
- Lifecycle: `ephemeral`.
- Use a new `build_id` (dd-mm-yy-NN).
- CI roles and secrets are already configured.

---

## Validation steps

### 1) PR plan

1. Update `envs/dev/terraform.tfvars` with a new `build_id`.
2. Open a PR.
3. Confirm the PR comment shows:
   - Plan summary (create/update/delete/replace/read counts)
   - Full plan (collapsible)

Expected result: PR plan completes successfully and comments on the PR.

---

### 2) Merge and apply

1. Merge the PR.
2. Run `Infra Terraform Apply (dev)` with:
   - `lifecycle=ephemeral`
   - `build_id=<new id>`
   - `new_build=true`
   - `confirm_apply=apply`

Expected result: apply guard accepts the PR plan (or the merged PR head SHA) and
the apply completes.

---

### 3) Bootstrap

Run `ci-bootstrap.yml` with the same `build_id` and:

- `config_source=repo`
- `confirm_irsa_apply=true`
- `bootstrap_only=false`
- `scale_down_after_bootstrap=false`

Expected result: bootstrap completes and IRSA service accounts are applied.

---

### 4) Teardown

Run `ci-teardown.yml` with the same `build_id` and:

- `cleanup_mode=delete`
- `force_delete_lbs=true` (default)

Expected result: teardown completes without subnet dependency errors.

---

### 5) Post-check (no orphans)

Run these checks from a trusted shell with AWS credentials:

```bash
aws eks list-clusters --region eu-west-2 --output table
aws ec2 describe-network-interfaces --region eu-west-2 \
  --filters Name=tag:BuildId,Values=<build_id> \
  --query 'NetworkInterfaces[].{Id:NetworkInterfaceId,Status:Status,Type:InterfaceType,Desc:Description}' \
  --output table
aws elbv2 describe-load-balancers --region eu-west-2 \
  --query 'LoadBalancers[].{Name:LoadBalancerName,Arn:LoadBalancerArn}' \
  --output table
```

Expected result: no cluster for the build and no tagged ENIs/LBs remain.

---

## Troubleshooting hints

- **Apply guard failure:** ensure a PR plan ran on the PR head SHA and the
  merged commit references that PR.
- **Teardown stuck on subnets:** verify LB ENIs are gone; if not, confirm
  cluster-scoped LB deletion is enabled.
- **State mismatch:** confirm `build_id` and `cluster_lifecycle` are consistent
  across plan, apply, bootstrap, and teardown.

---

## Notes

This validation is intentionally strict. If any step fails, fix the flow before
marking the platform stable.
