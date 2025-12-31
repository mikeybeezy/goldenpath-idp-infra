#!/usr/bin/env bash
set -euo pipefail

# Cleanup AWS Load Balancer Controller managed resources when the cluster is gone.
# Usage:
#   bootstrap/60_tear_down_clean_up/cleanup-managed-lb-resources.sh <cluster-name> <region>
#
# Dry-run by default. Set DRY_RUN=false to perform deletions.
# Optional: STACK_TAG to narrow to a single service.k8s.aws/stack value.

cluster_name="${1:-}"
region="${2:-}"
dry_run="${DRY_RUN:-true}"
stack_tag="${STACK_TAG:-}"
delete_cluster_tagged_sgs="${DELETE_CLUSTER_TAGGED_SGS:-false}"

if [[ -z "${cluster_name}" || -z "${region}" ]]; then
  echo "Usage: $0 <cluster-name> <region>" >&2
  echo "Set DRY_RUN=false to perform deletions." >&2
  exit 1
fi

failures=()

run_delete() {
  local desc="$1"
  shift
  if [[ "${dry_run}" == "true" ]]; then
    echo "[dry-run] ${desc}"
    return 0
  fi
  if ! "$@"; then
    failures+=("${desc}")
    return 1
  fi
}

echo "Managed LB cleanup starting (cluster=${cluster_name}, region=${region}, dry_run=${dry_run})"
if [[ -n "${stack_tag}" ]]; then
  echo "Stack filter: service.k8s.aws/stack=${stack_tag}"
fi
echo "Delete cluster-tagged security groups: ${delete_cluster_tagged_sgs}"

tag_filters=("Key=elbv2.k8s.aws/cluster,Values=${cluster_name}")
if [[ -n "${stack_tag}" ]]; then
  tag_filters+=("Key=service.k8s.aws/stack,Values=${stack_tag}")
fi

lb_arns=$(aws resourcegroupstaggingapi get-resources \
  --tag-filters "${tag_filters[@]}" \
  --resource-type-filters "elasticloadbalancing:loadbalancer" \
  --region "${region}" \
  --query "ResourceTagMappingList[].ResourceARN" --output text)

if [[ -n "${lb_arns}" ]]; then
  for arn in ${lb_arns}; do
    run_delete "Delete load balancer ${arn}" aws elbv2 delete-load-balancer --load-balancer-arn "${arn}" --region "${region}"
  done
else
  echo "No load balancers found for cluster tag."
fi

eni_rows=$(aws ec2 describe-network-interfaces \
  --filters "Name=tag:elbv2.k8s.aws/cluster,Values=${cluster_name}" \
  --region "${region}" \
  --query "NetworkInterfaces[].{Id:NetworkInterfaceId,Status:Status}" --output text)

if [[ -n "${eni_rows}" ]]; then
  while read -r eni_id eni_status; do
    if [[ -z "${eni_id}" ]]; then
      continue
    fi
    if [[ "${eni_status}" != "available" ]]; then
      echo "Skipping ENI ${eni_id} (status=${eni_status})"
      continue
    fi
    run_delete "Delete ENI ${eni_id}" aws ec2 delete-network-interface --network-interface-id "${eni_id}" --region "${region}"
  done <<< "${eni_rows}"
else
  echo "No ENIs found for cluster tag."
fi

sg_filters=(
  "Name=tag:service.k8s.aws/resource,Values=ManagedLBSecurityGroup"
  "Name=tag:elbv2.k8s.aws/cluster,Values=${cluster_name}"
)
if [[ -n "${stack_tag}" ]]; then
  sg_filters+=("Name=tag:service.k8s.aws/stack,Values=${stack_tag}")
fi

sg_ids=$(aws ec2 describe-security-groups \
  --filters "${sg_filters[@]}" \
  --region "${region}" \
  --query "SecurityGroups[].GroupId" --output text)

if [[ -n "${sg_ids}" ]]; then
  for sg_id in ${sg_ids}; do
    run_delete "Delete managed LB security group ${sg_id}" aws ec2 delete-security-group --group-id "${sg_id}" --region "${region}"
  done
else
  echo "No managed LB security groups found for cluster tag."
fi

if [[ "${delete_cluster_tagged_sgs}" == "true" ]]; then
  cluster_sg_ids=$(aws ec2 describe-security-groups \
    --filters "Name=tag:elbv2.k8s.aws/cluster,Values=${cluster_name}" \
    --region "${region}" \
    --query "SecurityGroups[?GroupName!=\`default\`].GroupId" --output text)

  if [[ -n "${cluster_sg_ids}" ]]; then
    for sg_id in ${cluster_sg_ids}; do
      run_delete "Delete cluster-tagged security group ${sg_id}" aws ec2 delete-security-group --group-id "${sg_id}" --region "${region}"
    done
  else
    echo "No cluster-tagged security groups found."
  fi
else
  echo "Skipping cluster-tagged security group cleanup (DELETE_CLUSTER_TAGGED_SGS=false)."
fi

if [[ "${#failures[@]}" -gt 0 ]]; then
  echo "Cleanup completed with failures:"
  for item in "${failures[@]}"; do
    echo "- ${item}"
  done
  exit 1
fi

echo "Managed LB cleanup finished."
