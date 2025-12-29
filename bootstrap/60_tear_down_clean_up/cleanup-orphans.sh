#!/usr/bin/env bash
set -euo pipefail

# Cleanup tagged orphaned AWS resources created by a failed build.
# Usage:
#   bootstrap/60_tear_down_clean_up/cleanup-orphans.sh <build-id> <region>
#
# Dry-run by default. Set DRY_RUN=false to execute deletions.

build_id="${1:-}"
region="${2:-}"
dry_run="${DRY_RUN:-true}"
state_bucket="${STATE_BUCKET:-}"
state_table="${STATE_TABLE:-}"

if [[ -z "${build_id}" || -z "${region}" ]]; then
  echo "Usage: $0 <build-id> <region>" >&2
  echo "Set DRY_RUN=false to perform deletions." >&2
  exit 1
fi

run() {
  if [[ "${dry_run}" == "true" ]]; then
    echo "[dry-run] $*"
  else
    eval "$@"
  fi
}

echo "Cleanup starting (BuildId=${build_id}, region=${region}, dry_run=${dry_run})"
if [[ -n "${state_bucket}" || -n "${state_table}" ]]; then
  echo "State context (bucket=${state_bucket:-unset}, table=${state_table:-unset})"
fi
echo "Safety: state backend resources (S3 bucket, DynamoDB lock table) are never modified."

# EKS: delete node groups first, then clusters.
eks_clusters=$(aws resourcegroupstaggingapi get-resources \
  --tag-filters "Key=BuildId,Values=${build_id}" \
  --resource-type-filters "eks:cluster" \
  --region "${region}" \
  --query "ResourceTagMappingList[].ResourceARN" --output text)

for arn in ${eks_clusters}; do
  cluster_name="${arn##*/}"
  nodegroups=$(aws eks list-nodegroups --cluster-name "${cluster_name}" --region "${region}" --query "nodegroups[]" --output text)
  for ng in ${nodegroups}; do
    run aws eks delete-nodegroup --cluster-name "${cluster_name}" --nodegroup-name "${ng}" --region "${region}"
  done
  run aws eks delete-cluster --name "${cluster_name}" --region "${region}"
done

# Load balancers (classic and v2).
lb_arns=$(aws resourcegroupstaggingapi get-resources \
  --tag-filters "Key=BuildId,Values=${build_id}" \
  --resource-type-filters "elasticloadbalancing:loadbalancer" \
  --region "${region}" \
  --query "ResourceTagMappingList[].ResourceARN" --output text)

for arn in ${lb_arns}; do
  if [[ "${arn}" == *"/app/"* || "${arn}" == *"/net/"* || "${arn}" == *"/gateway/"* ]]; then
    run aws elbv2 delete-load-balancer --load-balancer-arn "${arn}" --region "${region}"
  else
    lb_name="${arn##*/}"
    run aws elb delete-load-balancer --load-balancer-name "${lb_name}" --region "${region}"
  fi
done

# EC2 instances.
instances=$(aws ec2 describe-instances \
  --filters "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "Reservations[].Instances[].InstanceId" --output text)
if [[ -n "${instances}" ]]; then
  run aws ec2 terminate-instances --instance-ids ${instances} --region "${region}"
fi

# NAT gateways.
nat_gws=$(aws ec2 describe-nat-gateways \
  --filter "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "NatGateways[].NatGatewayId" --output text)
for nat in ${nat_gws}; do
  run aws ec2 delete-nat-gateway --nat-gateway-id "${nat}" --region "${region}"
done

# Elastic IPs.
eips=$(aws ec2 describe-addresses \
  --filters "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "Addresses[].AllocationId" --output text)
for eip in ${eips}; do
  run aws ec2 release-address --allocation-id "${eip}" --region "${region}"
done

# Route tables (skip main).
rt_ids=$(aws ec2 describe-route-tables \
  --filters "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "RouteTables[].{Id:RouteTableId,Main:Associations[?Main==\`true\`]|[0].Main}" \
  --output text)
if [[ -n "${rt_ids}" ]]; then
  while read -r rtb main; do
    if [[ "${main}" != "True" ]]; then
      run aws ec2 delete-route-table --route-table-id "${rtb}" --region "${region}"
    fi
  done <<< "${rt_ids}"
fi

# Subnets.
subnets=$(aws ec2 describe-subnets \
  --filters "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "Subnets[].SubnetId" --output text)
for subnet in ${subnets}; do
  run aws ec2 delete-subnet --subnet-id "${subnet}" --region "${region}"
done

# Security groups (skip default).
sgs=$(aws ec2 describe-security-groups \
  --filters "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "SecurityGroups[?GroupName!=\`default\`].GroupId" --output text)
for sg in ${sgs}; do
  run aws ec2 delete-security-group --group-id "${sg}" --region "${region}"
done

# Internet gateways (detach then delete).
igws=$(aws ec2 describe-internet-gateways \
  --filters "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "InternetGateways[].InternetGatewayId" --output text)
for igw in ${igws}; do
  vpcs=$(aws ec2 describe-internet-gateways --internet-gateway-ids "${igw}" --region "${region}" --query "InternetGateways[].Attachments[].VpcId" --output text)
  for vpc in ${vpcs}; do
    run aws ec2 detach-internet-gateway --internet-gateway-id "${igw}" --vpc-id "${vpc}" --region "${region}"
  done
  run aws ec2 delete-internet-gateway --internet-gateway-id "${igw}" --region "${region}"
done

# VPCs.
vpcs=$(aws ec2 describe-vpcs \
  --filters "Name=tag:BuildId,Values=${build_id}" \
  --region "${region}" \
  --query "Vpcs[].VpcId" --output text)
for vpc in ${vpcs}; do
  run aws ec2 delete-vpc --vpc-id "${vpc}" --region "${region}"
done

echo "Cleanup finished (dry_run=${dry_run})"
