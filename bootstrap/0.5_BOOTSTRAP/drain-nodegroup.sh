#!/usr/bin/env bash
set -euo pipefail

# Drain nodes in a specific EKS node group before resizing or replacement.
# Usage:
#   bootstrap-scripts/drain-nodegroup.sh <nodegroup-name>

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

echo "Draining nodes in ${nodegroup}"
kubectl drain ${nodes} --ignore-daemonsets --delete-emptydir-data --grace-period=60

echo "Drain complete. Proceed with node group update."
