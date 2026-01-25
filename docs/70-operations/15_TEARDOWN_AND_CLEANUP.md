---
id: 15_TEARDOWN_AND_CLEANUP
title: Teardown and Cleanup Commands
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
  - 04_LB_FINALIZER_STUCK
  - 06_LB_ENI_ORPHANS
  - 06_REBUILD_SEQUENCE
  - 09_CI_TEARDOWN_RECOVERY_V2
  - 10_INFRA_FAILURE_MODES
  - 16_INFRA_Build_ID_Strategy_Decision
  - 70_OPERATIONS_README
  - ADR-0038-platform-teardown-orphan-cleanup-gate
  - ADR-0041-platform-orphan-cleanup-deletion-order
  - ADR-0043-platform-teardown-lb-eni-wait
  - ADR-0045-platform-teardown-lb-delete-default
  - ADR-0047-platform-teardown-destroy-timeout-retry
  - ADR-0048-platform-teardown-version-selector
  - ADR-0053-platform-storage-lifecycle-separation
  - ADR-0057-platform-ci-terraform-force-unlock-workflow
  - ADR-0164-teardown-v3-enhanced-reliability
  - BOOTSTRAP_10_BOOTSTRAP_README
  - RB-0006-lb-eni-orphans
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
category: compliance
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# Teardown and Cleanup Commands

Doc contract:

- Purpose: Provide teardown guidance and manual cleanup commands.
- Owner: platform
- Status: reference
- Review cadence: as needed
- Related: docs/70-operations/10_INFRA_FAILURE_MODES.md, docs/70-operations/runbooks/09_CI_TEARDOWN_RECOVERY_V2.md, docs/70-operations/runbooks/06_LB_ENI_ORPHANS.md, docs/70-operations/runbooks/04_LB_FINALIZER_STUCK.md, docs/adrs/ADR-0043-platform-teardown-lb-eni-wait.md

Last updated: 2026-01-21

This page lists manual AWS CLI commands to find and remove lingering
resources that block teardown. Use the teardown runner and cleanup scripts
first; use these commands when Terraform or the scripts cannot finish the job.

## Teardown runner (recommended)

The teardown runner drains node groups, removes dependencies, and then
destroys the cluster.

Teardown runner versions:

- `goldenpath-idp-teardown-v5.sh` (v5, default)
- `goldenpath-idp-teardown-v4.sh` (v4)
- `goldenpath-idp-teardown-v3.sh` (v3)
- `goldenpath-idp-teardown-v2.sh` (v2)
- `goldenpath-idp-teardown.sh` (v1, legacy)
- Makefile selection: set `TEARDOWN_VERSION=v1|v2|v3|v4|v5` (CI exposes the same input).

Why this order matters:

- Node groups keep ENIs, ASGs, and security groups alive.
- LoadBalancer Services keep AWS LBs and SGs attached.
- Removing those first prevents dependency errors during VPC/subnet deletes.

Argo CD cleanup options (for deleting apps like Kong that recreate LBs):

- **Option 1: Argo API token** (CI secret)
  - Pros: non-interactive, stable, least brittle; good for syncs/ops.
  - Cons: token lifecycle management and secret storage.
- **Option 2: pull admin password from Kubernetes**
  - Pros: simple; no token setup.
  - Cons: depends on secret existence; less secure; can break if rotated/deleted.
- **Option 3: delete Application CR via kubectl**
  - Pros: avoids Argo auth entirely; best for teardown/CI cleanup.
  - Cons: bypasses Argo workflows/audit trail; it is a hard delete.

Decision:

- For teardown/CI cleanup, we use **Option 3** to avoid auth failures and keep teardown deterministic.

Teardown strategy decision:

- **Default**: try Terraform destroy when `TF_DIR` is set.
- **Fallback**: if Terraform cannot run (no kube access) or fails, you can

  enable AWS deletion with `TF_DESTROY_FALLBACK_AWS=true` (default: false).

Tradeoffs:

- Terraform keeps state clean but requires a live cluster for k8s resources.
- AWS fallback is more reliable for cleanup but can leave Terraform state stale.

```bash

TEARDOWN_CONFIRM=true \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v5.sh <cluster> <region>

```text

Select v5 via Makefile (default):

```bash

TEARDOWN_VERSION=v5 make teardown ENV=dev BUILD_ID=<build_id> CLUSTER=<cluster> REGION=<region>

```text

If drains are blocked by PodDisruptionBudgets, enable PDB relaxation:

```bash

TEARDOWN_CONFIRM=true RELAX_PDB=true \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v5.sh <cluster> <region>

```text

Drain timeout behavior:

- The drain step uses `DRAIN_TIMEOUT` (default `300s`).
- On timeout, it relaxes CoreDNS PDBs and retries once.

```bash

TEARDOWN_CONFIRM=true RELAX_PDB=true DRAIN_TIMEOUT=300s \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v5.sh <cluster> <region>

```text

Progress heartbeats:

- The teardown runner prints a heartbeat every 30s while:
  - LoadBalancer services are deleting.
  - Node groups are deleting.
  - Nodegroup/cluster waits are running (`aws eks wait`).
  - The cluster is deleting.
  - Terraform destroy is running (when TF_DIR is set).
  - Orphan cleanup is running (when CLEANUP_ORPHANS=true and mode is not `none`).

Set `HEARTBEAT_INTERVAL` to change the cadence (default `30` seconds).

LoadBalancer cleanup retries:

- The runner re-attempts LoadBalancer Service deletion in case AWS is slow to

  reconcile.

- `LB_CLEANUP_ATTEMPTS` controls how many retry loops run (default `5`).
- `LB_CLEANUP_INTERVAL` controls the delay between loops (default `20` seconds).
- `LB_CLEANUP_MAX_WAIT` caps the LoadBalancer wait loop (default `900` seconds).
- If Services remain after the wait, v5 removes stuck finalizers by default
  (`FORCE_DELETE_LB_FINALIZERS=true`) to avoid teardown hangs when the LB
  controller is not available. This is safe only for teardown runs where the
  Service should be deleted.
- If Kubernetes access is unavailable, v5 skips Kubernetes cleanup and performs
  AWS-only LoadBalancer cleanup before continuing to destroy.

LoadBalancer ENI wait (prevents stuck subnet deletes):

- After LoadBalancer Services are gone, the runner waits for any
  network load balancer ENIs to disappear.
- `WAIT_FOR_LB_ENIS` controls this wait (default `true`).
- `LB_ENI_WAIT_MAX` caps the ENI wait loop (default `LB_CLEANUP_MAX_WAIT`).
- `FORCE_DELETE_LBS` defaults to `true` and deletes remaining Kubernetes load
  balancers if ENIs do not disappear in time. Deletion is scoped to LBs tagged
  with `elbv2.k8s.aws/cluster=<cluster_name>`.
- CI exposes this as the `force_delete_lbs` workflow input (default `true`).
- Ensure the teardown role can call `elasticloadbalancing:DeleteLoadBalancer`,
  `elasticloadbalancing:DescribeTags`, and `ec2:DescribeNetworkInterfaces` (see
  `docs/10-governance/policies/ci-teardown-extra-permissions.json`).
- Recovery note: if a partial teardown left ENIs behind, re-run teardown with
  `FORCE_DELETE_LBS=true` after confirming only disposable LBs remain.

ENI consistency constraints:

- ENIs for managed services (ELB) cannot be detached or deleted directly.
- ENIs may remain in-use after LB deletion due to eventual consistency.
- ENI counts per LB vary with load and can change during teardown.
- Tag coverage on ENIs is not guaranteed; cluster scoping should be enforced on LBs.

Runbook: `docs/70-operations/runbooks/06_LB_ENI_ORPHANS.md`

```bash

TEARDOWN_CONFIRM=true LB_CLEANUP_ATTEMPTS=8 LB_CLEANUP_INTERVAL=30 \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v5.sh <cluster> <region>

```text

Force delete remaining cluster LBs (optional override):

```bash

TEARDOWN_CONFIRM=true FORCE_DELETE_LBS=true \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v5.sh <cluster> <region>

```text

Orphan cleanup modes:

- `ORPHAN_CLEANUP_MODE=delete` deletes BuildId-tagged resources.
- `ORPHAN_CLEANUP_MODE=dry_run` lists resources only.
- `ORPHAN_CLEANUP_MODE=none` skips cleanup (even if `CLEANUP_ORPHANS=true`).
- CI uses the `cleanup_mode` workflow input to set this.
- Orphan cleanup never deletes the Terraform state S3 bucket or DynamoDB lock table.
- Orphan cleanup targets EKS, LBs, EC2, NAT, EIPs, ENIs, route tables, subnets, SGs, IGWs, VPCs, and IAM roles.

Recommended deletion order:

1) EKS node groups → EKS cluster
2) Load balancers
3) EC2 instances
4) ENIs (unattached only)
5) IAM roles (BuildId-tagged)
6) NAT gateways
7) Elastic IPs
8) Route tables (detach associations, skip main)
9) Subnets
10) Security groups (non-default)
11) Internet gateways (detach then delete)
12) VPCs

Terraform destroy guard:

- `REQUIRE_KUBE_FOR_TF_DESTROY` (default `true`) verifies kube access before

  Terraform destroy to avoid localhost Kubernetes provider errors.

- `REMOVE_K8S_SA_FROM_STATE` (default `true`) removes Kubernetes service

  accounts from state before Terraform destroy, preventing teardown from
  failing when kube access is missing or unstable. The teardown runner will
  attempt a lightweight `terraform init` if state access fails.

- `TF_AUTO_APPROVE` (default `false`) uses `-auto-approve` for Terraform

  destroy. The Makefile teardown targets set this to `true` by default.

- `TF_DESTROY_MAX_WAIT` (default `1200`) caps Terraform destroy runtime. If the
  timeout is hit, teardown re-checks LoadBalancer ENIs and retries once.

- `TF_DESTROY_RETRY_ON_LB_CLEANUP` (default `true`) enables the retry after LB
  cleanup when Terraform destroy fails or times out.

- If Terraform destroy fails or is skipped, the runner falls back to AWS

  cluster deletion when `TF_DESTROY_FALLBACK_AWS=true` (default).

Argo CD application cleanup:

- Teardown deletes the configured Argo CD Application before deleting
  LoadBalancer Services to prevent GitOps reconciliation from recreating them.
- `DELETE_ARGO_APP` (default `true`) skips or enables this step.
- `ARGO_APP_NAMESPACE` (default `kong-system`) selects the namespace.
- `ARGO_APP_NAME` (default `dev-kong`) selects the application.

Recovery after partial teardown (state drift):

- If teardown exits early, Kubernetes service accounts may be deleted while
  Terraform state still tracks them. PR plans will try to recreate them and
  may fail with Unauthorized during refresh.
- The teardown runner now attempts a best-effort state cleanup on exit when
  `TF_DIR` is set and `REMOVE_K8S_SA_FROM_STATE=true`.
- Use the resume target to finish cleanup when a teardown was interrupted.
- CI teardown runs automatically attempt `teardown-resume` after a failure.
- CI teardown uses a `cleanup_mode` input (`delete`, `dry_run`, `none`).
  Use `none` to skip, or `dry_run` for discovery without deletes.
- Use the `CI Force Unlock` workflow to release a stuck Terraform lock only
  after confirming no Terraform jobs are active for the same state.
- Use the `CI Managed LB Cleanup` workflow when the cluster is gone but VPC
  deletion fails due to AWS Load Balancer Controller managed security groups,
  ENIs, or LBs tagged to the cluster.

Resume teardown (recommended):

```bash

make teardown-resume ENV=dev BUILD_ID=<build_id> CLUSTER=<cluster> REGION=<region>

```text

Manual state cleanup (if you only need to reset k8s service accounts):

```bash

bootstrap/60_tear_down_clean_up/remove-k8s-service-accounts-from-state.sh envs/dev

```text

Service-account-only changes vs full apply:

- If you only need Kubernetes service accounts (LB controller/autoscaler), use

  the targeted apply path (`ENABLE_TF_K8S_RESOURCES=true`) to avoid touching
  compute/VPC resources.

- Running a full apply/destroy can cascade into EC2/SG changes; if a standalone

  instance is still attached to a security group, SG deletion will fail.
  This is the most common reason teardown appears “stuck” even though you only
  intended to adjust service accounts.

Makefile shortcut:

```bash

make teardown ENV=dev CLUSTER=<cluster> REGION=<region>

```text

Timed teardown (logs to `logs/build-timings/` and writes to `docs/build-timings.csv`):

```bash

make timed-teardown ENV=dev BUILD_ID=<build_id> CLUSTER=<cluster> REGION=<region>

```text

Terraform destroy instead of `aws eks delete-cluster`:

```bash

TEARDOWN_CONFIRM=true TF_DIR=envs/dev \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v5.sh <cluster> <region>

```text

`TF_DIR` can be relative; the teardown script resolves it from the repo root.

For the naming/tagging approach that makes teardown deterministic, see
`docs/40-delivery/16_INFRA_Build_ID_Strategy_Decision.md`.

Replace values in angle brackets and set the region. You can also export IDs as
environment variables to reuse them across commands:

```bash

export AWS_REGION=eu-west-2
export VPC_ID=vpc-xxxxxxxxxxxxxxxxx

```text

Optional exports after discovery:

```bash

export LB_ARN=arn:aws:elasticloadbalancing:...
export NAT_ID=nat-...
export VPCE_ID=vpce-...
export IGW_ID=igw-...
export RTB_ID=rtb-...
export SUBNET_ID=subnet-...

```text

## Load balancers (ALB/NLB)

List:

```bash

aws elbv2 describe-load-balancers --region "$AWS_REGION" \
  --query 'LoadBalancers[?VpcId==`'"$VPC_ID"'`].[LoadBalancerArn,DNSName]' \
  --output table
w```

Delete:

```bash

aws elbv2 delete-load-balancer --load-balancer-arn "${LB_ARN:-<lb-arn>}" --region "$AWS_REGION"

```text

Classic ELB (if any):

```bash

aws elb describe-load-balancers --region "$AWS_REGION" \
  --query 'LoadBalancerDescriptions[?VPCId==`'"$VPC_ID"'`].[LoadBalancerName,DNSName]' \
  --output table
aws elb delete-load-balancer --load-balancer-name <elb-name> --region "$AWS_REGION"

```text

## Target groups, listeners, rules

List target groups:

```bash

aws elbv2 describe-target-groups --region "$AWS_REGION" \
  --query 'TargetGroups[?VpcId==`'"$VPC_ID"'`].[TargetGroupArn,TargetGroupName]' \
  --output table

```text

## NAT gateways and EIPs

```bash

aws ec2 describe-nat-gateways --region "$AWS_REGION" \
  --filter Name=vpc-id,Values="$VPC_ID" \
  --query 'NatGateways[].NatGatewayId' --output text
aws ec2 delete-nat-gateway --nat-gateway-id "${NAT_ID:-<nat-id>}" --region "$AWS_REGION"

```text

Release EIPs after NAT is gone:

```bash

aws ec2 describe-addresses --region "$AWS_REGION" \
  --query 'Addresses[?AssociationId!=null].[AllocationId,PublicIp]' \
  --output table
aws ec2 release-address --allocation-id <alloc-id> --region "$AWS_REGION"

```text

## VPC endpoints

```bash

aws ec2 describe-vpc-endpoints --region "$AWS_REGION" \
  --filters Name=vpc-id,Values="$VPC_ID" \
  --query 'VpcEndpoints[].VpcEndpointId' --output text
aws ec2 delete-vpc-endpoints --vpc-endpoint-ids "${VPCE_ID:-<vpce-id>}" --region "$AWS_REGION"

```text

## Network interfaces (ENIs)

```bash

aws ec2 describe-network-interfaces --region "$AWS_REGION" \
  --filters Name=vpc-id,Values="$VPC_ID" \
  --query 'NetworkInterfaces[].{Id:NetworkInterfaceId,Desc:Description,Status:Status,Attachment:Attachment.InstanceId}' \
  --output table

```text

If ENIs remain, delete the owning service (LB, NAT, endpoint, or instance)
before retrying.
NLB ENIs appear as `ELB net/...` descriptions and will block subnet deletes
until the load balancer is fully removed.

## Subnets, route tables, and gateways

Once dependencies are gone:

```bash

aws ec2 describe-subnets --region "$AWS_REGION" \
  --filters Name=vpc-id,Values="$VPC_ID" \
  --query 'Subnets[].SubnetId' --output text
aws ec2 delete-subnet --subnet-id "${SUBNET_ID:-<subnet-id>}" --region "$AWS_REGION"

```text

```bash

aws ec2 describe-route-tables --region "$AWS_REGION" \
  --filters Name=vpc-id,Values="$VPC_ID" \
  --query 'RouteTables[].RouteTableId' --output text
aws ec2 delete-route-table --route-table-id "${RTB_ID:-<rtb-id>}" --region "$AWS_REGION"

```text

```bash

aws ec2 describe-internet-gateways --region "$AWS_REGION" \
  --filters Name=attachment.vpc-id,Values="$VPC_ID" \
  --query 'InternetGateways[].InternetGatewayId' --output text
aws ec2 detach-internet-gateway --internet-gateway-id "${IGW_ID:-<igw-id>}" --vpc-id "$VPC_ID" --region "$AWS_REGION"
aws ec2 delete-internet-gateway --internet-gateway-id "${IGW_ID:-<igw-id>}" --region "$AWS_REGION"

```text

## Final VPC delete

```bash

aws ec2 delete-vpc --vpc-id "$VPC_ID" --region "$AWS_REGION"

```text

## Notes

- Always delete Kubernetes LoadBalancer services first to avoid dangling LBs.
- Some resources take several minutes to fully release.
