# Load Balancer ENIs Block Subnet Deletion

## Purpose

Restore teardown when subnet deletion fails because network load balancer (NLB)
ENIs remain in use after Kubernetes LoadBalancer Services were deleted.

## Symptoms

- `terraform destroy` fails with `DependencyViolation` on subnets.
- `aws ec2 describe-network-interfaces` shows ENIs with
  `Type=network_load_balancer`.
- Kubernetes LoadBalancer Services are already deleted.

## Why this happens

- ENIs are owned by managed services (ELB), so manual detach/delete is blocked.
- AWS cleanup is eventually consistent; ENIs can persist after LB deletion.
- ENI counts scale with load and can vary per LB.
- Tag coverage is not guaranteed on every ENI.

## Recovery checklist (recommended)

1) Confirm no LoadBalancer Services remain:

```bash
kubectl get svc -A | rg LoadBalancer
```

2) List ENIs in the affected subnets:

```bash
aws ec2 describe-network-interfaces --region eu-west-2 \
  --filters Name=subnet-id,Values=<subnet-a>,<subnet-b> \
  --query 'NetworkInterfaces[].{Id:NetworkInterfaceId,Type:InterfaceType,Desc:Description}' \
  --output table
```

3) Identify cluster-scoped LBs and delete them:

```bash
aws elbv2 describe-load-balancers --region eu-west-2 \
  --query 'LoadBalancers[].LoadBalancerArn' --output text | tr '\t' '\n' \
  | while read -r arn; do
      tag="$(aws elbv2 describe-tags --region eu-west-2 --resource-arns "$arn" \
        --query 'TagDescriptions[0].Tags[?Key==`elbv2.k8s.aws/cluster`].Value | [0]' \
        --output text)"
      if [[ "$tag" == "<cluster-name>" ]]; then
        aws elbv2 delete-load-balancer --region eu-west-2 --load-balancer-arn "$arn"
      fi
    done
```

4) Wait for ENIs to disappear, then retry teardown.

## Operational defaults (CI)

- `LB_CLEANUP_ATTEMPTS=5`
- `LB_CLEANUP_INTERVAL=20`
- `LB_CLEANUP_MAX_WAIT=900`
- `LB_ENI_WAIT_INTERVAL=30`
- `LB_ENI_WAIT_MAX=900`
- `FORCE_DELETE_LBS=true`
- `TF_DESTROY_MAX_WAIT=1200`
- `TF_DESTROY_RETRY_ON_LB_CLEANUP=true`

## Extended timeout option

If ENIs remain after 15 minutes, increase the wait window:

```bash
LB_ENI_WAIT_MAX=2700
```

## Escalation

If ENIs persist beyond 48 hours and no matching LBs remain, open an AWS Support
case with the ENI IDs and VPC/subnet details.

## Related

- `docs/runbooks/04_LB_FINALIZER_STUCK.md`
- `docs/15_TEARDOWN_AND_CLEANUP.md`
- `docs/adrs/ADR-0047-platform-teardown-destroy-timeout-retry.md`
