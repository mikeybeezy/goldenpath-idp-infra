#!/usr/bin/env bash
set -euo pipefail

cluster_name="${1:-}"
region="${2:-}"
vpc_id="${3:-}"
service_account_name="${4:-aws-load-balancer-controller}"
service_account_namespace="${5:-kube-system}"

if [[ -z "${cluster_name}" || -z "${region}" || -z "${vpc_id}" ]]; then
  echo "Usage: $0 <cluster_name> <region> <vpc_id> [service_account_name] [service_account_namespace]" >&2
  exit 1
fi

# Ensure kubeconfig is pointed at the target cluster.
aws eks update-kubeconfig --region "${region}" --name "${cluster_name}"

# Ensure the IRSA-backed service account exists before installing the controller.
if ! kubectl -n "${service_account_namespace}" get sa "${service_account_name}" >/dev/null 2>&1; then
  echo "ServiceAccount ${service_account_namespace}/${service_account_name} not found." >&2
  echo "Create it with the correct IAM role for the AWS Load Balancer Controller, then rerun." >&2
  exit 1
fi

# Add and update the EKS Helm repo.
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# Install or upgrade the AWS Load Balancer Controller.
helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
  --namespace "${service_account_namespace}" \
  --set clusterName="${cluster_name}" \
  --set region="${region}" \
  --set vpcId="${vpc_id}" \
  --set serviceAccount.create=false \
  --set serviceAccount.name="${service_account_name}"

# Wait for the controller deployment to be ready.
kubectl -n "${service_account_namespace}" rollout status deployment/aws-load-balancer-controller --timeout=180s
