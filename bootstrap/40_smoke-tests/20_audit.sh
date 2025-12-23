#!/usr/bin/env bash
set -euo pipefail

cluster_name="${1:-}"
region="${2:-}"

if [[ -z "${cluster_name}" || -z "${region}" ]]; then
  echo "Usage: $0 <cluster_name> <region>" >&2
  exit 1
fi

timestamp="$(date -u +"%Y%m%dT%H%M%SZ")"
out_dir="bootstrap/40_smoke-tests/audit"
mkdir -p "${out_dir}"
report_md="${out_dir}/${cluster_name}-${timestamp}.md"

{
  echo "# Cluster Audit"
  echo
  echo "- Cluster: ${cluster_name}"
  echo "- Region: ${region}"
  echo "- Timestamp (UTC): ${timestamp}"
  echo
  echo "## Phase 1: EKS control plane"
  echo
  aws eks describe-cluster --name "${cluster_name}" --region "${region}" --output table
  echo
  echo "### Add-ons"
  echo
  aws eks list-addons --cluster-name "${cluster_name}" --region "${region}" --output table
  echo
  while read -r addon; do
    [[ -z "${addon}" ]] && continue
    echo "#### ${addon}"
    aws eks describe-addon --cluster-name "${cluster_name}" --addon-name "${addon}" --region "${region}" --output table
    echo
  done < <(aws eks list-addons --cluster-name "${cluster_name}" --region "${region}" --output text | awk '{print $2}' | tr '\t' '\n')

  echo "## Phase 2: Kubernetes core"
  echo
  kubectl get nodes -o wide
  echo
  kubectl get pods -A
  echo
  kubectl get deployments -n kube-system
  echo
  kubectl get apiservices | awk 'NR==1 || /metrics|v1beta1.metrics.k8s.io/'
  echo
} > "${report_md}"

echo "Audit written to ${report_md}"
