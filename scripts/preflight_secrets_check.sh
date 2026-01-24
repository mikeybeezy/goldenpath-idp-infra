#!/usr/bin/env bash
# ---
# id: SCRIPT-0053
# type: script
# owner: platform-team
# status: active
# maturity: 2
# dry_run:
#   supported: false
#   command_hint: N/A
# test:
#   runner: shellcheck
#   command: shellcheck scripts/preflight_secrets_check.sh
#   evidence: declared
# risk_profile:
#   production_impact: medium
#   security_risk: low
#   coupling_risk: low
# ---
# -----------------------------------------------------------------------------
# Preflight Secrets Check
# Validates that required secrets exist and have non-placeholder values
#
# Usage: ./preflight_secrets_check.sh <environment> [--fail-on-placeholder]
#
# Exit codes:
#   0 - All secrets valid
#   1 - Missing secrets or missing AWSCURRENT version
#   2 - Placeholder values detected (only with --fail-on-placeholder)
# -----------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV="${1:-dev}"
FAIL_ON_PLACEHOLDER="${2:-}"
REGION="${AWS_REGION:-eu-west-2}"

# Secrets required for Tier 2+ apps
REQUIRED_SECRETS=(
  "goldenpath/${ENV}/backstage/secrets"
  "goldenpath/${ENV}/keycloak/admin"
)

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "Preflight: Checking secrets for environment '${ENV}'..."
echo ""

has_missing=false
has_placeholder=false

for secret_name in "${REQUIRED_SECRETS[@]}"; do
  echo -n "  Checking ${secret_name}... "

  # Check if secret exists
  if ! aws secretsmanager describe-secret \
    --secret-id "${secret_name}" \
    --region "${REGION}" \
    --query 'ARN' \
    --output text >/dev/null 2>&1; then
    echo -e "${RED}MISSING${NC}"
    has_missing=true
    continue
  fi

  # Check if secret has AWSCURRENT version (i.e., has a value)
  version_ids=$(aws secretsmanager list-secret-version-ids \
    --secret-id "${secret_name}" \
    --region "${REGION}" \
    --query "Versions[?contains(VersionStages, 'AWSCURRENT')].VersionId" \
    --output text 2>/dev/null || echo "")

  if [[ -z "${version_ids}" ]]; then
    echo -e "${RED}NO VALUE${NC}"
    has_missing=true
    continue
  fi

  # Check for placeholder values
  secret_value=$(aws secretsmanager get-secret-value \
    --secret-id "${secret_name}" \
    --region "${REGION}" \
    --query 'SecretString' \
    --output text 2>/dev/null || echo "")

  if [[ "${secret_value}" == *"PLACEHOLDER"* ]]; then
    echo -e "${YELLOW}PLACEHOLDER${NC}"
    has_placeholder=true
  else
    echo -e "${GREEN}OK${NC}"
  fi
done

echo ""

# Exit based on findings
if [[ "${has_missing}" == "true" ]]; then
  echo -e "${RED}ERROR: Some secrets are missing or have no value.${NC}"
  echo "Run 'make deploy ENV=${ENV}' to create secrets with initial values."
  exit 1
fi

if [[ "${has_placeholder}" == "true" ]]; then
  echo "┌────────────────────────────────────────────────────────────────────┐"
  echo "│  ⚠️  ACTION REQUIRED: Update placeholder secrets in AWS Console    │"
  echo "├────────────────────────────────────────────────────────────────────┤"
  echo "│  goldenpath/${ENV}/backstage/secrets → GITHUB_TOKEN                │"
  echo "│  goldenpath/${ENV}/keycloak/admin   → admin credentials            │"
  echo "└────────────────────────────────────────────────────────────────────┘"
  echo ""
  echo "ExternalSecrets will remain in SecretSyncedError until updated."

  if [[ "${FAIL_ON_PLACEHOLDER}" == "--fail-on-placeholder" ]]; then
    echo -e "${RED}CI mode: Failing due to placeholder values.${NC}"
    exit 2
  fi
fi

echo -e "${GREEN}Preflight secrets check passed.${NC}"
exit 0
