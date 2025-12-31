#!/usr/bin/env bash
set -euo pipefail

# Pre-destroy cleanup for Kubernetes LoadBalancer services.
# This prevents AWS from keeping ELB/NLB resources (and SGs) attached during teardown.
# Usage:
#   bootstrap/60_tear_down_clean_up/pre-destroy-cleanup.sh <cluster-name> <region> [--yes]

cluster_name="${1:-}"
region="${2:-}"
confirm="${3:-}"
kubectl_timeout="${KUBECTL_REQUEST_TIMEOUT:-10s}"

if [[ -z "${cluster_name}" || -z "${region}" ]]; then
  echo "Usage: $0 <cluster-name> <region> [--yes]" >&2
  exit 1
fi

aws eks update-kubeconfig --name "${cluster_name}" --region "${region}"

services="$(kubectl --request-timeout="${kubectl_timeout}" get svc -A -o jsonpath='{range .items[?(@.spec.type=="LoadBalancer")]}{.metadata.namespace}/{.metadata.name}{"\n"}{end}')"

if [[ -z "${services}" ]]; then
  echo "No LoadBalancer services found."
  exit 0
fi

echo "LoadBalancer services:"
echo "${services}"

if [[ "${confirm}" != "--yes" ]]; then
  echo "Re-run with --yes to delete these services before destroy."
  exit 0
fi

while read -r svc; do
  ns="${svc%%/*}"
  name="${svc##*/}"
  echo "Deleting ${ns}/${name}"
  kubectl --request-timeout="${kubectl_timeout}" -n "${ns}" delete svc "${name}" || true
done <<< "${services}"

echo "LoadBalancer service deletion requested. Wait for AWS LBs to fully remove before destroy."
