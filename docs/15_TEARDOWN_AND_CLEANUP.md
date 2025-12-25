# Teardown and Cleanup Commands

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
```

If drains are blocked by PodDisruptionBudgets, enable PDB relaxation:

```bash
TEARDOWN_CONFIRM=true RELAX_PDB=true \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>
```

Drain timeout behavior:

- The drain step uses `DRAIN_TIMEOUT` (default `300s`).
- On timeout, it relaxes CoreDNS PDBs and retries once.

```bash
TEARDOWN_CONFIRM=true RELAX_PDB=true DRAIN_TIMEOUT=300s \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>
```

Progress heartbeats:

- The teardown runner prints a heartbeat every 30s while:
  - LoadBalancer services are deleting.
  - Node groups are deleting.
  - Nodegroup/cluster waits are running (`aws eks wait`).
  - The cluster is deleting.
  - Terraform destroy is running (when TF_DIR is set).
  - Orphan cleanup is running (when CLEANUP_ORPHANS=true).

Set `HEARTBEAT_INTERVAL` to change the cadence (default `30` seconds).

LoadBalancer cleanup retries:

- The runner re-attempts LoadBalancer Service deletion in case AWS is slow to
  reconcile.
- `LB_CLEANUP_ATTEMPTS` controls how many retry loops run (default `5`).
- `LB_CLEANUP_INTERVAL` controls the delay between loops (default `20` seconds).

```bash
TEARDOWN_CONFIRM=true LB_CLEANUP_ATTEMPTS=8 LB_CLEANUP_INTERVAL=30 \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>
```

Terraform destroy guard:

- `REQUIRE_KUBE_FOR_TF_DESTROY` (default `true`) verifies kube access before
  Terraform destroy to avoid localhost Kubernetes provider errors.
- `REMOVE_K8S_SA_FROM_STATE` (default `true`) removes Kubernetes service
  accounts from state when kube access is missing so Terraform destroy can
  continue.
- If Terraform destroy fails or is skipped, the runner falls back to AWS
  cluster deletion when `TF_DESTROY_FALLBACK_AWS=true` (default).

Makefile shortcut:

```bash
make teardown ENV=dev CLUSTER=<cluster> REGION=<region>
```

Terraform destroy instead of `aws eks delete-cluster`:

```bash
TEARDOWN_CONFIRM=true TF_DIR=envs/dev \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>
```

For the naming/tagging approach that makes teardown deterministic, see
`docs/16_INFRA_Build_ID_Strategy_Decision.md`.

Replace values in angle brackets and set the region. You can also export IDs as
environment variables to reuse them across commands:

```bash
export AWS_REGION=eu-west-2
export VPC_ID=vpc-xxxxxxxxxxxxxxxxx
```

Optional exports after discovery:

```bash
export LB_ARN=arn:aws:elasticloadbalancing:...
export NAT_ID=nat-...
export VPCE_ID=vpce-...
export IGW_ID=igw-...
export RTB_ID=rtb-...
export SUBNET_ID=subnet-...
```

## Load balancers (ALB/NLB)

List:

```bash
aws elbv2 describe-load-balancers --region "$AWS_REGION" \
  --query 'LoadBalancers[?VpcId==`'"$VPC_ID"'`].[LoadBalancerArn,DNSName]' \
  --output table
```

Delete:

```bash
aws elbv2 delete-load-balancer --load-balancer-arn "${LB_ARN:-<lb-arn>}" --region "$AWS_REGION"
```

Classic ELB (if any):

```bash
aws elb describe-load-balancers --region "$AWS_REGION" \
  --query 'LoadBalancerDescriptions[?VPCId==`'"$VPC_ID"'`].[LoadBalancerName,DNSName]' \
  --output table
aws elb delete-load-balancer --load-balancer-name <elb-name> --region "$AWS_REGION"
```

## Target groups, listeners, rules

List target groups:

```bash
aws elbv2 describe-target-groups --region "$AWS_REGION" \
  --query 'TargetGroups[?VpcId==`'"$VPC_ID"'`].[TargetGroupArn,TargetGroupName]' \
  --output table
```

## NAT gateways and EIPs

```bash
aws ec2 describe-nat-gateways --region "$AWS_REGION" \
  --filter Name=vpc-id,Values="$VPC_ID" \
  --query 'NatGateways[].NatGatewayId' --output text
aws ec2 delete-nat-gateway --nat-gateway-id "${NAT_ID:-<nat-id>}" --region "$AWS_REGION"
```

Release EIPs after NAT is gone:

```bash
aws ec2 describe-addresses --region "$AWS_REGION" \
  --query 'Addresses[?AssociationId!=null].[AllocationId,PublicIp]' \
  --output table
aws ec2 release-address --allocation-id <alloc-id> --region "$AWS_REGION"
```

## VPC endpoints

```bash
aws ec2 describe-vpc-endpoints --region "$AWS_REGION" \
  --filters Name=vpc-id,Values="$VPC_ID" \
  --query 'VpcEndpoints[].VpcEndpointId' --output text
aws ec2 delete-vpc-endpoints --vpc-endpoint-ids "${VPCE_ID:-<vpce-id>}" --region "$AWS_REGION"
```

## Network interfaces (ENIs)

```bash
aws ec2 describe-network-interfaces --region "$AWS_REGION" \
  --filters Name=vpc-id,Values="$VPC_ID" \
  --query 'NetworkInterfaces[].{Id:NetworkInterfaceId,Desc:Description,Status:Status,Attachment:Attachment.InstanceId}' \
  --output table
```

If ENIs remain, delete the owning service (LB, NAT, endpoint, or instance)
before retrying.

## Subnets, route tables, and gateways

Once dependencies are gone:

```bash
aws ec2 describe-subnets --region "$AWS_REGION" \
  --filters Name=vpc-id,Values="$VPC_ID" \
  --query 'Subnets[].SubnetId' --output text
aws ec2 delete-subnet --subnet-id "${SUBNET_ID:-<subnet-id>}" --region "$AWS_REGION"
```

```bash
aws ec2 describe-route-tables --region "$AWS_REGION" \
  --filters Name=vpc-id,Values="$VPC_ID" \
  --query 'RouteTables[].RouteTableId' --output text
aws ec2 delete-route-table --route-table-id "${RTB_ID:-<rtb-id>}" --region "$AWS_REGION"
```

```bash
aws ec2 describe-internet-gateways --region "$AWS_REGION" \
  --filters Name=attachment.vpc-id,Values="$VPC_ID" \
  --query 'InternetGateways[].InternetGatewayId' --output text
aws ec2 detach-internet-gateway --internet-gateway-id "${IGW_ID:-<igw-id>}" --vpc-id "$VPC_ID" --region "$AWS_REGION"
aws ec2 delete-internet-gateway --internet-gateway-id "${IGW_ID:-<igw-id>}" --region "$AWS_REGION"
```

## Final VPC delete

```bash
aws ec2 delete-vpc --vpc-id "$VPC_ID" --region "$AWS_REGION"
```

## Notes

- Always delete Kubernetes LoadBalancer services first to avoid dangling LBs.
- Some resources take several minutes to fully release.
