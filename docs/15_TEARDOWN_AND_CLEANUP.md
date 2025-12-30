# Teardown and Cleanup Commands

Last updated: 2025-12-29

This page lists manual AWS CLI commands to find and remove lingering
resources that block teardown. Use the teardown runner and cleanup scripts
first; use these commands when Terraform or the scripts cannot finish the job.

## Teardown runner (recommended)

The teardown runner drains node groups, removes dependencies, and then
destroys the cluster.

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
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>

```text

If drains are blocked by PodDisruptionBudgets, enable PDB relaxation:

```bash

TEARDOWN_CONFIRM=true RELAX_PDB=true \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>

```text

Drain timeout behavior:

- The drain step uses `DRAIN_TIMEOUT` (default `300s`).
- On timeout, it relaxes CoreDNS PDBs and retries once.

```bash

TEARDOWN_CONFIRM=true RELAX_PDB=true DRAIN_TIMEOUT=300s \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>

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

LoadBalancer ENI wait (prevents stuck subnet deletes):

- After LoadBalancer Services are gone, the runner waits for any
  network load balancer ENIs to disappear.
- `WAIT_FOR_LB_ENIS` controls this wait (default `true`).
- `LB_ENI_WAIT_MAX` caps the ENI wait loop (default `LB_CLEANUP_MAX_WAIT`).
- `FORCE_DELETE_LBS=true` is a break-glass option that deletes remaining
  Kubernetes load balancers if ENIs do not disappear in time.
- CI exposes this as the `force_delete_lbs` workflow input.
- Ensure the teardown role can call `elasticloadbalancing:DeleteLoadBalancer`
  and `ec2:DescribeNetworkInterfaces` (see
  `docs/policies/ci-teardown-extra-permissions.json`).

```bash

TEARDOWN_CONFIRM=true LB_CLEANUP_ATTEMPTS=8 LB_CLEANUP_INTERVAL=30 \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>

```text

Break-glass ENI cleanup:

```bash

TEARDOWN_CONFIRM=true FORCE_DELETE_LBS=true \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>

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
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>

```text

`TF_DIR` can be relative; the teardown script resolves it from the repo root.

For the naming/tagging approach that makes teardown deterministic, see
`docs/16_INFRA_Build_ID_Strategy_Decision.md`.

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
