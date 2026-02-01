#!/bin/bash
# ---
# id: SCRIPT-0009
# type: script
# owner: platform-team
# status: deprecated
# maturity: 2
# deprecated_by: _build-and-release.yml
# deprecation_reason: CI use consolidated into canonical workflow with inline build/push + security gates
# dry_run:
#   supported: true
#   command_hint: --dry-run
# test:
#   runner: shellcheck
#   command: shellcheck scripts/ecr-build-push.sh
#   evidence: declared
# risk_profile:
#   production_impact: low
#   security_risk: low
#   coupling_risk: low
# ---
# -----------------------------------------------------------------------------
# ECR Build & Push Utility
#
# DEPRECATED: 2026-02-01
# This script is deprecated for CI use. The canonical workflow
# _build-and-release.yml contains inline build/push with security gates
# (Trivy, SBOM, Gitleaks). Use the thin caller template instead:
#   docs/templates/workflows/delivery.yml
#
# This script is retained for LOCAL DEVELOPMENT use only.
#
# Purpose:
#   Standardizes the image build and push process across the platform.
#   Ensures consistent tagging (Git SHA + Version) and proper ECR authentication.
#
# Usage:
#   ./ecr-build-push.sh --registry URL --name NAME --sha SHA [--version VERSION] [--region REGION]
#
# Example:
#   ./ecr-build-push.sh --registry 123456789.dkr.ecr.eu-west-2.amazonaws.com \
#                        --name my-app --sha a1b2c3d --version 1.0.4
# -----------------------------------------------------------------------------

set -e

# Defaults
REGION="eu-west-2"
VERSION=""

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --registry) REGISTRY="$2"; shift ;;
        --name) NAME="$2"; shift ;;
        --sha) SHA="$2"; shift ;;
        --version) VERSION="$2"; shift ;;
        --region) REGION="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Validate required inputs
if [[ -z "$REGISTRY" ]] || [[ -z "$NAME" ]] || [[ -z "$SHA" ]]; then
    echo "❌ Error: Missing required arguments (--registry, --name, --sha)"
    echo "Usage: $0 --registry <url> --name <name> --sha <sha> [--version <version>]"
    exit 1
fi

FULL_REPO_URL="${REGISTRY}/${NAME}"

echo "🚀 Starting build and push for: ${FULL_REPO_URL}"

# 1. Authenticate to ECR
echo "🔑 Authenticating to ECR..."
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$REGISTRY"

# 2. Build Image
echo "🏗️  Building image: ${NAME}:${SHA}"
docker build -t "${FULL_REPO_URL}:${SHA}" .

# 3. Add Version Tag if provided
if [[ -n "$VERSION" ]]; then
    echo "🏷️  Adding version tag: ${VERSION}"
    docker tag "${FULL_REPO_URL}:${SHA}" "${FULL_REPO_URL}:${VERSION}"
fi

# 4. Push Tags
echo "📤 Pushing tags to ECR..."
docker push "${FULL_REPO_URL}:${SHA}"

if [[ -n "$VERSION" ]]; then
    docker push "${FULL_REPO_URL}:${VERSION}"
fi

echo "✅ Successfully built and pushed ${NAME} to ECR"
echo "   - URL: ${FULL_REPO_URL}:${SHA}"
[[ -n "$VERSION" ]] && echo "   - URL: ${FULL_REPO_URL}:${VERSION}"
