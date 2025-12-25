#!/usr/bin/env bash
set -euo pipefail

# Remove Kubernetes service accounts from Terraform state so destroy can proceed
# after the cluster is gone.

tf_dir="${1:-}"

if [[ -z "${tf_dir}" ]]; then
  echo "Usage: $0 <terraform-dir>" >&2
  exit 1
fi

if ! command -v terraform >/dev/null; then
  echo "Missing required command: terraform" >&2
  exit 1
fi

state_list="$(terraform -chdir="${tf_dir}" state list 2>/dev/null || true)"
if [[ -z "${state_list}" ]]; then
  echo "Terraform state list failed or empty; attempting init in ${tf_dir}..."
  terraform -chdir="${tf_dir}" init -input=false -upgrade=false >/dev/null 2>&1 || true
  state_list="$(terraform -chdir="${tf_dir}" state list 2>/dev/null || true)"
fi
state_items="$(echo "${state_list}" | \
  grep -E '^(kubernetes_service_account_v1\.|module\.eks\\[0\\]\\.kubernetes_service_account_v1)' || true)"

known_addresses=(
  "kubernetes_service_account_v1.aws_load_balancer_controller[0]"
  "kubernetes_service_account_v1.cluster_autoscaler[0]"
  "module.eks[0].kubernetes_service_account_v1.aws_load_balancer_controller[0]"
  "module.eks[0].kubernetes_service_account_v1.cluster_autoscaler[0]"
)

combined="$(printf "%s\n" "${state_items}" "${known_addresses[@]}" | awk 'NF' | sort -u)"

echo "Removing Kubernetes service accounts from Terraform state (best effort):"
while read -r addr; do
  [[ -z "${addr}" ]] && continue
  echo "  - ${addr}"
  terraform -chdir="${tf_dir}" state rm "${addr}" >/dev/null 2>&1 || true
done <<< "${combined}"

echo "Kubernetes service accounts removed from state."

remaining="$(terraform -chdir="${tf_dir}" state list 2>/dev/null | grep -E 'kubernetes_service_account_v1' || true)"
if [[ -n "${remaining}" ]]; then
  echo "Warning: Kubernetes service account resources still in state:" >&2
  echo "${remaining}" >&2
  exit 1
fi
