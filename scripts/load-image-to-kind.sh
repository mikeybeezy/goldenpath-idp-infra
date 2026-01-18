#!/bin/bash
# load-image-to-kind.sh
# Pulls an image from ECR and loads it directly into Kind cluster
# This bypasses the need for ECR pull secrets in the cluster
#
# Usage: ./scripts/load-image-to-kind.sh [image] [kind-cluster]
#
# Example:
#   ./scripts/load-image-to-kind.sh hello-goldenpath-idp:latest kind

set -euo pipefail

IMAGE="${1:-hello-goldenpath-idp:latest}"
KIND_CLUSTER="${2:-kind}"
AWS_REGION="${AWS_REGION:-eu-west-2}"
AWS_ACCOUNT="${AWS_ACCOUNT:-339712971032}"
ECR_REGISTRY="${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com"
FULL_IMAGE="${ECR_REGISTRY}/${IMAGE}"

echo "Loading image into Kind cluster: ${KIND_CLUSTER}"
echo "Image: ${FULL_IMAGE}"

# Login to ECR
echo "Authenticating to ECR..."
aws ecr get-login-password --region "${AWS_REGION}" | \
  docker login --username AWS --password-stdin "${ECR_REGISTRY}"

# Pull the image
echo "Pulling image from ECR..."
docker pull "${FULL_IMAGE}"

# Load into Kind
echo "Loading image into Kind cluster..."
kind load docker-image "${FULL_IMAGE}" --name "${KIND_CLUSTER}"

echo ""
echo "Image loaded successfully!"
echo ""
echo "Update your deployment to use:"
echo "  image: ${FULL_IMAGE}"
echo "  imagePullPolicy: Never  # Important for Kind-loaded images"
