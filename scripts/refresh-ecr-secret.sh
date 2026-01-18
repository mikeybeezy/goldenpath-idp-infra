#!/bin/bash
# ---
# id: SCRIPT-0050
# type: script
# owner: platform-team
# status: active
# maturity: 2
# dry_run:
#   supported: false
# test:
#   runner: manual
#   command: ./scripts/refresh-ecr-secret.sh apps
#   evidence: manual
# risk_profile:
#   production_impact: low
#   security_risk: low
#   coupling_risk: low
# ---
#
# refresh-ecr-secret.sh
# Refreshes the ECR pull secret for local Kind cluster
# ECR tokens expire after 12 hours, so run this before deploying
#
# Usage: ./scripts/refresh-ecr-secret.sh [namespace]
#
# Prerequisites:
#   - AWS CLI configured with ECR access
#   - kubectl configured for Kind cluster

set -euo pipefail

NAMESPACE="${1:-apps}"
AWS_REGION="${AWS_REGION:-eu-west-2}"
AWS_ACCOUNT="${AWS_ACCOUNT:-593517239005}"
ECR_REGISTRY="${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "Refreshing ECR pull secret for namespace: ${NAMESPACE}"
echo "ECR Registry: ${ECR_REGISTRY}"

# Ensure namespace exists
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

# Get ECR password
ECR_PASSWORD=$(aws ecr get-login-password --region "${AWS_REGION}")

# Create/update the secret
kubectl create secret docker-registry ecr-pull-secret \
  --docker-server="${ECR_REGISTRY}" \
  --docker-username=AWS \
  --docker-password="${ECR_PASSWORD}" \
  --namespace="${NAMESPACE}" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "ECR pull secret refreshed successfully in namespace: ${NAMESPACE}"
echo ""
echo "Note: ECR tokens expire after 12 hours. Re-run this script if pulls fail."
