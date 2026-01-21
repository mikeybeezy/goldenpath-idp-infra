#!/usr/bin/env bash
# ---
# id: SCRIPT-0052
# type: script
# owner: platform-team
# status: active
# maturity: 2
# dry_run:
#   supported: false
#   command_hint: N/A
# test:
#   runner: shellcheck
#   command: shellcheck scripts/rds_secrets_preflight.sh
#   evidence: declared
# risk_profile:
#   production_impact: medium
#   security_risk: low
#   coupling_risk: low
# ---
set -euo pipefail

env="${1:-}"
if [ -z "$env" ]; then
  echo "Usage: $0 <env>" >&2
  exit 1
fi

rds_dir="envs/${env}-rds"
tfvars="${rds_dir}/terraform.tfvars"

if [ ! -d "$rds_dir" ] || [ ! -f "$tfvars" ]; then
  echo "RDS environment directory not found: ${rds_dir}" >&2
  echo "Available: $(ls -d envs/*-rds 2>/dev/null || echo 'none')" >&2
  exit 1
fi

region=$(
  awk -F= '/^[[:space:]]*aws_region[[:space:]]*=/{gsub(/"|[[:space:]]/,"",$2);print $2;exit}' "$tfvars"
)
if [ -z "$region" ]; then
  echo "ERROR: aws_region not found in ${tfvars}" >&2
  exit 1
fi

state_has() {
  terraform -chdir="$rds_dir" state list 2>/dev/null | grep -Fxq "$1"
}

restore_and_import() {
  local addr="$1"
  local secret="$2"

  if ! aws secretsmanager describe-secret --secret-id "$secret" --region "$region" >/dev/null 2>&1; then
    return 0
  fi

  local deleted_date
  deleted_date=$(
    aws secretsmanager describe-secret \
      --secret-id "$secret" \
      --region "$region" \
      --query "DeletedDate" \
      --output text 2>/dev/null || true
  )

  if [ -n "$deleted_date" ] && [ "$deleted_date" != "None" ]; then
    echo "Restoring secret ${secret} (scheduled for deletion)"
    aws secretsmanager restore-secret --secret-id "$secret" --region "$region" >/dev/null
  fi

  if ! state_has "$addr"; then
    echo "Importing secret ${secret} into state (${addr})"
    terraform -chdir="$rds_dir" import "$addr" "$secret" >/dev/null
  fi
}

restore_and_import "aws_secretsmanager_secret.master" "goldenpath/${env}/rds/master"

app_keys=$(
  awk '
    BEGIN{in_block=0}
    /^[[:space:]]*application_databases[[:space:]]*=/ {in_block=1}
    in_block && /^[[:space:]]*}/ {in_block=0}
    in_block && /^[[:space:]]*[A-Za-z0-9_-]+[[:space:]]*=[[:space:]]*{/ {
      key=$1; gsub(/[[:space:]]/, "", key); gsub(/=.*/, "", key); print key;
    }
  ' "$tfvars"
)

for key in $app_keys; do
  restore_and_import "aws_secretsmanager_secret.app[\"${key}\"]" "goldenpath/${env}/${key}/postgres"
done
