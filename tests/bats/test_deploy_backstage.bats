#!/usr/bin/env bats
# Tests for scripts/deploy-backstage.sh
# SCRIPT-0008: Backstage Deployment Script
#
# Run with: bats tests/bats/test_deploy_backstage.bats

load 'helpers/common'

SCRIPT_UNDER_TEST="${PROJECT_ROOT}/scripts/deploy-backstage.sh"

setup() {
  export TEST_TEMP_DIR=$(mktemp -d)
  export PATH="${TEST_TEMP_DIR}/bin:$PATH"
  mkdir -p "${TEST_TEMP_DIR}/bin"

  # Track mock calls
  export MOCK_CALLS_FILE="${TEST_TEMP_DIR}/mock_calls.log"
  touch "$MOCK_CALLS_FILE"

  # Create mock helm chart directory
  mkdir -p "${TEST_TEMP_DIR}/gitops/helm/backstage/chart"
  touch "${TEST_TEMP_DIR}/gitops/helm/backstage/chart/Chart.yaml"
}

teardown() {
  rm -rf "$TEST_TEMP_DIR"
}

# Create mock kubectl
create_mock_kubectl() {
  local crd_exists="${1:-true}"
  cat > "${TEST_TEMP_DIR}/bin/kubectl" << EOF
#!/bin/bash
echo "kubectl \$@" >> "\$MOCK_CALLS_FILE"
if [[ "\$1" == "get" && "\$2" == "customresourcedefinition" ]]; then
  if [[ "$crd_exists" == "true" ]]; then
    exit 0
  else
    exit 1
  fi
fi
exit 0
EOF
  chmod +x "${TEST_TEMP_DIR}/bin/kubectl"
}

# Create mock helm
create_mock_helm() {
  cat > "${TEST_TEMP_DIR}/bin/helm" << 'EOF'
#!/bin/bash
echo "helm $@" >> "$MOCK_CALLS_FILE"
exit 0
EOF
  chmod +x "${TEST_TEMP_DIR}/bin/helm"
}

# Create mock python3
create_mock_python() {
  cat > "${TEST_TEMP_DIR}/bin/python3" << 'EOF'
#!/bin/bash
echo "python3 $@" >> "$MOCK_CALLS_FILE"
exit 0
EOF
  chmod +x "${TEST_TEMP_DIR}/bin/python3"
}

@test "deploy_backstage: script file exists" {
  assert_file_exists "$SCRIPT_UNDER_TEST"
}

@test "deploy_backstage: script is executable" {
  [[ -x "$SCRIPT_UNDER_TEST" ]]
}

@test "deploy_backstage: has required metadata header" {
  run head -20 "$SCRIPT_UNDER_TEST"
  assert_success
  assert_output_contains "id: SCRIPT-0008"
  assert_output_contains "type: script"
}

@test "deploy_backstage: creates backstage namespace" {
  create_mock_kubectl "true"
  create_mock_helm
  create_mock_python

  # Run from temp dir with mock helm chart
  cd "$TEST_TEMP_DIR"
  mkdir -p scripts/lib
  touch scripts/lib/vq_logger.py

  # Copy script to temp and run
  cp "$SCRIPT_UNDER_TEST" ./deploy-backstage.sh

  run bash ./deploy-backstage.sh

  # Check namespace creation was attempted
  grep -q "kubectl.*namespace backstage" "$MOCK_CALLS_FILE"
}

@test "deploy_backstage: checks for CloudNativePG CRD" {
  create_mock_kubectl "true"
  create_mock_helm
  create_mock_python

  cd "$TEST_TEMP_DIR"
  mkdir -p scripts/lib
  touch scripts/lib/vq_logger.py
  cp "$SCRIPT_UNDER_TEST" ./deploy-backstage.sh

  run bash ./deploy-backstage.sh

  # Check CRD check was performed
  grep -q "kubectl get customresourcedefinition" "$MOCK_CALLS_FILE"
}

@test "deploy_backstage: installs CloudNativePG when missing" {
  create_mock_kubectl "false"  # CRD doesn't exist
  create_mock_helm
  create_mock_python

  cd "$TEST_TEMP_DIR"
  mkdir -p scripts/lib
  touch scripts/lib/vq_logger.py
  cp "$SCRIPT_UNDER_TEST" ./deploy-backstage.sh

  run bash ./deploy-backstage.sh

  # Check helm was called to install CNPG
  grep -q "helm.*cnpg" "$MOCK_CALLS_FILE" || grep -q "Installing CloudNativePG" "$output"
}

@test "deploy_backstage: deploys backstage helm chart" {
  create_mock_kubectl "true"
  create_mock_helm
  create_mock_python

  cd "$TEST_TEMP_DIR"
  mkdir -p scripts/lib
  touch scripts/lib/vq_logger.py
  cp "$SCRIPT_UNDER_TEST" ./deploy-backstage.sh

  run bash ./deploy-backstage.sh

  # Check helm upgrade --install was called for backstage
  grep -q "helm upgrade --install backstage" "$MOCK_CALLS_FILE"
}

@test "deploy_backstage: handles missing GH_TOKEN gracefully" {
  create_mock_kubectl "true"
  create_mock_helm
  create_mock_python

  cd "$TEST_TEMP_DIR"
  mkdir -p scripts/lib
  touch scripts/lib/vq_logger.py
  cp "$SCRIPT_UNDER_TEST" ./deploy-backstage.sh

  unset GH_TOKEN

  run bash ./deploy-backstage.sh

  assert_success
  assert_output_contains "GH_TOKEN not set"
}

@test "deploy_backstage: creates GitHub secret when GH_TOKEN set" {
  create_mock_kubectl "true"
  create_mock_helm
  create_mock_python

  cd "$TEST_TEMP_DIR"
  mkdir -p scripts/lib
  touch scripts/lib/vq_logger.py
  cp "$SCRIPT_UNDER_TEST" ./deploy-backstage.sh

  export GH_TOKEN="ghp_test_token_12345"

  run bash ./deploy-backstage.sh

  # Check secret creation was attempted
  grep -q "kubectl create secret" "$MOCK_CALLS_FILE"
}

@test "deploy_backstage: records VQ heartbeat when logger exists" {
  create_mock_kubectl "true"
  create_mock_helm
  create_mock_python

  cd "$TEST_TEMP_DIR"
  mkdir -p scripts/lib
  touch scripts/lib/vq_logger.py
  cp "$SCRIPT_UNDER_TEST" ./deploy-backstage.sh

  run bash ./deploy-backstage.sh

  # Check VQ logger was called
  grep -q "python3.*vq_logger" "$MOCK_CALLS_FILE" || assert_output_contains "Recording Value Heartbeat"
}

@test "deploy_backstage: prints success message on completion" {
  create_mock_kubectl "true"
  create_mock_helm
  create_mock_python

  cd "$TEST_TEMP_DIR"
  mkdir -p scripts/lib
  touch scripts/lib/vq_logger.py
  cp "$SCRIPT_UNDER_TEST" ./deploy-backstage.sh

  run bash ./deploy-backstage.sh

  assert_success
  assert_output_contains "Backstage deployed successfully"
}

@test "deploy_backstage: provides port-forward instructions" {
  create_mock_kubectl "true"
  create_mock_helm
  create_mock_python

  cd "$TEST_TEMP_DIR"
  mkdir -p scripts/lib
  touch scripts/lib/vq_logger.py
  cp "$SCRIPT_UNDER_TEST" ./deploy-backstage.sh

  run bash ./deploy-backstage.sh

  assert_success
  assert_output_contains "port-forward"
  assert_output_contains "7007"
}
