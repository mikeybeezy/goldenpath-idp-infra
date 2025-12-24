#!/usr/bin/env bash
set -euo pipefail

# Ensure required CLI tools are available before bootstrapping.
required_tools=(aws kubectl helm)

for tool in "${required_tools[@]}"; do
  # Fail fast with a clear message if any tool is missing.
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "Missing required tool: ${tool}" >&2
    exit 1
  fi
done

# Print versions for auditability.
aws --version
kubectl version --client
helm version
