#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE' >&2
Resolve the effective EKS cluster name from terraform.tfvars.

Usage:
  scripts/resolve-cluster-name.sh [path/to/terraform.tfvars]

Resolution order for tfvars path:
  1) argument (if provided)
  2) TF_DIR/terraform.tfvars (if TF_DIR is set)
  3) envs/$ENV/terraform.tfvars (if ENV is set)
  4) envs/dev/terraform.tfvars
USAGE
}

tfvars_path="${1:-}"
if [[ -z "${tfvars_path}" ]]; then
  if [[ -n "${TF_DIR:-}" ]]; then
    tfvars_path="${TF_DIR}/terraform.tfvars"
  elif [[ -n "${ENV:-}" ]]; then
    tfvars_path="envs/${ENV}/terraform.tfvars"
  else
    tfvars_path="envs/dev/terraform.tfvars"
  fi
fi

if [[ ! -f "${tfvars_path}" ]]; then
  echo "tfvars not found: ${tfvars_path}" >&2
  usage
  exit 1
fi

read_top_var() {
  local key="$1"
  awk -F'=' -v k="${key}" '{
    line=$0
    sub(/#.*/,"",line)
    if (line ~ /^[[:space:]]*$/) next
    split(line, parts, "=")
    lhs=parts[1]; gsub(/[[:space:]]/,"",lhs)
    if (lhs==k) {
      val=parts[2]
      sub(/#.*/,"",val)
      gsub(/"/,"",val)
      gsub(/[[:space:]]/,"",val)
      print val
      exit
    }
  }' "${tfvars_path}"
}

read_eks_cluster_name() {
  awk 'BEGIN{in_block=0;depth=0}{
    line=$0
    sub(/#.*/,"",line)
    if (line ~ /^[[:space:]]*eks_config[[:space:]]*=/) {in_block=1}
    if (in_block) {
      if (line ~ /{/) depth++
      if (line ~ /}/) {depth--; if (depth<=0) in_block=0}
      if (line ~ /^[[:space:]]*cluster_name[[:space:]]*=/) {
        split(line, parts, "=")
        val=parts[2]
        sub(/#.*/,"",val)
        gsub(/"/,"",val)
        gsub(/[[:space:]]/,"",val)
        print val
        exit
      }
    }
  }' "${tfvars_path}"
}

environment="$(read_top_var "environment")"
name_prefix="$(read_top_var "name_prefix")"
cluster_lifecycle="${CLUSTER_LIFECYCLE:-$(read_top_var "cluster_lifecycle")}"
build_id="${BUILD_ID:-$(read_top_var "build_id")}"
eks_cluster_name="$(read_eks_cluster_name)"

if [[ -z "${cluster_lifecycle}" ]]; then
  cluster_lifecycle="persistent"
fi

base_name_prefix="${name_prefix}"
if [[ -z "${base_name_prefix}" ]]; then
  if [[ -n "${environment}" ]]; then
    base_name_prefix="goldenpath-${environment}"
  fi
fi

cluster_base="${eks_cluster_name}"
if [[ -z "${cluster_base}" ]]; then
  if [[ -n "${base_name_prefix}" ]]; then
    cluster_base="${base_name_prefix}-eks"
  fi
fi

if [[ -z "${cluster_base}" ]]; then
  echo "Unable to resolve cluster name from ${tfvars_path}." >&2
  echo "Set eks_config.cluster_name or environment/name_prefix." >&2
  exit 1
fi

if [[ "${cluster_lifecycle}" == "ephemeral" && -n "${build_id}" ]]; then
  echo "${cluster_base}-${build_id}"
else
  echo "${cluster_base}"
fi
