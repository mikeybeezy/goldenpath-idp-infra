#!/usr/bin/env bash
set -euo pipefail

# Preflight checks for EKS node group creation.
# Usage:
#   bootstrap/00_prereqs/10_eks_preflight.sh <cluster-name> <region> <vpc-id> <private-subnet-ids> <node-role-arn> <instance-type>

cluster_name="${1:-}"
region="${2:-}"
vpc_id="${3:-}"
private_subnets="${4:-}"
node_role_arn="${5:-}"
instance_type="${6:-}"

if [[ -z "${cluster_name}" || -z "${region}" || -z "${vpc_id}" || -z "${private_subnets}" || -z "${node_role_arn}" || -z "${instance_type}" ]]; then
  echo "Usage: $0 <cluster-name> <region> <vpc-id> <private-subnet-ids> <node-role-arn> <instance-type>" >&2
  echo "Example: $0 goldenpath-dev-eks eu-west-2 vpc-abc subnet-a,subnet-b arn:aws:iam::123:role/role t3.small" >&2
  exit 1
fi

IFS=',' read -r -a subnet_ids <<< "${private_subnets}"

require_cmd() {
  if ! command -v "$1" >/dev/null; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

require_cmd aws
require_cmd kubectl

echo "Preflight checks for ${cluster_name} in ${region}"

# Check cluster endpoint access settings.
endpoint_public="$(aws eks describe-cluster --name "${cluster_name}" --region "${region}" --query 'cluster.resourcesVpcConfig.endpointPublicAccess' --output text)"
endpoint_private="$(aws eks describe-cluster --name "${cluster_name}" --region "${region}" --query 'cluster.resourcesVpcConfig.endpointPrivateAccess' --output text)"
echo "Cluster endpoint public=${endpoint_public} private=${endpoint_private}"

# Check private subnet route tables for NAT.
echo "Checking NAT routes for private subnets..."
for subnet_id in "${subnet_ids[@]}"; do
  rt_id="$(aws ec2 describe-route-tables --filters Name=association.subnet-id,Values="${subnet_id}" --region "${region}" --query 'RouteTables[0].RouteTableId' --output text)"
  if [[ "${rt_id}" == "None" || -z "${rt_id}" ]]; then
    rt_id="$(aws ec2 describe-route-tables --filters Name=association.main,Values=true Name=vpc-id,Values="${vpc_id}" --region "${region}" --query 'RouteTables[0].RouteTableId' --output text)"
  fi
  nat_route="$(aws ec2 describe-route-tables --route-table-ids "${rt_id}" --region "${region}" --query 'RouteTables[0].Routes[?DestinationCidrBlock==`0.0.0.0/0` && NatGatewayId!=null]' --output text)"
  if [[ -z "${nat_route}" ]]; then
    echo "No NAT route found for subnet ${subnet_id} (route table ${rt_id})." >&2
    exit 1
  fi
done

# Check node role policies.
echo "Checking node IAM role policies..."
role_name="${node_role_arn##*/}"
policies="$(aws iam list-attached-role-policies --role-name "${role_name}" --query 'AttachedPolicies[].PolicyArn' --output text)"
required=(
  "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
)
for policy in "${required[@]}"; do
  if ! echo "${policies}" | grep -q "${policy}"; then
    echo "Missing policy on node role: ${policy}" >&2
    exit 1
  fi
done

# Check instance type availability in region.
echo "Checking instance type availability: ${instance_type}"
available="$(aws ec2 describe-instance-type-offerings --location-type region --filters Name=instance-type,Values="${instance_type}" --region "${region}" --query 'InstanceTypeOfferings[].InstanceType' --output text)"
if [[ -z "${available}" ]]; then
  echo "Instance type ${instance_type} not available in ${region}." >&2
  exit 1
fi

# Optional: quick node readiness check if cluster already exists.
aws eks update-kubeconfig --name "${cluster_name}" --region "${region}" >/dev/null 2>&1 || true
ready_nodes="$(kubectl get nodes --no-headers 2>/dev/null | awk '$2 == "Ready" {count++} END {print count+0}')"
echo "Ready nodes: ${ready_nodes}"

echo "Preflight checks passed."
