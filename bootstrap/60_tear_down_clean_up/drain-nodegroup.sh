#!/usr/bin/env bash
set -euo pipefail

# Drain nodes in a specific EKS node group before resizing or replacement.
# Usage:
#   RELAX_PDB=true bootstrap/60_tear_down_clean_up/drain-nodegroup.sh <nodegroup-name>

nodegroup="${1:-}"

if [[ -z "${nodegroup}" ]]; then
  echo "Usage: $0 <nodegroup-name>" >&2
  exit 1
fi

nodes="$(kubectl get nodes -l eks.amazonaws.com/nodegroup="${nodegroup}" -o name)"

if [[ -z "${nodes}" ]]; then
  echo "No nodes found for nodegroup ${nodegroup}."
  exit 0
fi

echo "Cordoning nodes in ${nodegroup}"
kubectl cordon ${nodes}

if [[ "${RELAX_PDB:-false}" == "true" ]]; then
  echo "Relaxing CoreDNS PDB constraints for teardown..."
  if kubectl -n kube-system get deployment coredns >/dev/null 2>&1; then
    kubectl -n kube-system scale deployment coredns --replicas=1 || true
  fi
  if kubectl -n kube-system get pdb coredns >/dev/null 2>&1; then
    kubectl -n kube-system delete pdb coredns || true
  fi
fi

echo "Draining nodes in ${nodegroup}"
drain_timeout="${DRAIN_TIMEOUT:-300s}"
if ! kubectl drain ${nodes} --ignore-daemonsets --delete-emptydir-data --grace-period=60 --timeout="${drain_timeout}"; then
  echo "Drain timed out after ${drain_timeout}. Retrying with relaxed PDBs..."
  RELAX_PDB=true
  if kubectl -n kube-system get deployment coredns >/dev/null 2>&1; then
    kubectl -n kube-system scale deployment coredns --replicas=1 || true
  fi
  if kubectl -n kube-system get pdb coredns >/dev/null 2>&1; then
    kubectl -n kube-system delete pdb coredns || true
  fi
  kubectl drain ${nodes} --ignore-daemonsets --delete-emptydir-data --grace-period=60 --timeout="${drain_timeout}"
fi

echo "Drain complete. Proceed with node group update."
