#!/usr/bin/env bats
# Tests for scripts/ecr-build-push.sh
# SCRIPT-0009: ECR Build & Push Utility
#
# Run with: bats tests/bats/test_ecr_build_push.bats

load 'helpers/common'

SCRIPT_UNDER_TEST="${PROJECT_ROOT}/scripts/ecr-build-push.sh"

setup() {
  export TEST_TEMP_DIR=$(mktemp -d)
  export PATH="${TEST_TEMP_DIR}/bin:$PATH"
  mkdir -p "${TEST_TEMP_DIR}/bin"

  # Track mock calls
  export MOCK_CALLS_FILE="${TEST_TEMP_DIR}/mock_calls.log"
  touch "$MOCK_CALLS_FILE"
}

teardown() {
  rm -rf "$TEST_TEMP_DIR"
}

# Create mock aws command
create_mock_aws() {
  cat > "${TEST_TEMP_DIR}/bin/aws" << 'EOF'
#!/bin/bash
echo "aws $@" >> "$MOCK_CALLS_FILE"
if [[ "$1" == "ecr" && "$2" == "get-login-password" ]]; then
  echo "mock-password"
fi
exit 0
EOF
  chmod +x "${TEST_TEMP_DIR}/bin/aws"
}

# Create mock docker command
create_mock_docker() {
  cat > "${TEST_TEMP_DIR}/bin/docker" << 'EOF'
#!/bin/bash
echo "docker $@" >> "$MOCK_CALLS_FILE"
exit 0
EOF
  chmod +x "${TEST_TEMP_DIR}/bin/docker"
}

@test "ecr_build_push: script file exists" {
  assert_file_exists "$SCRIPT_UNDER_TEST"
}

@test "ecr_build_push: fails without required args" {
  run bash "$SCRIPT_UNDER_TEST"
  assert_failure
  assert_output_contains "Missing required arguments"
}

@test "ecr_build_push: fails without --registry" {
  run bash "$SCRIPT_UNDER_TEST" --name my-app --sha abc123
  assert_failure
  assert_output_contains "Missing required arguments"
}

@test "ecr_build_push: fails without --name" {
  run bash "$SCRIPT_UNDER_TEST" --registry 123.ecr.amazonaws.com --sha abc123
  assert_failure
  assert_output_contains "Missing required arguments"
}

@test "ecr_build_push: fails without --sha" {
  run bash "$SCRIPT_UNDER_TEST" --registry 123.ecr.amazonaws.com --name my-app
  assert_failure
  assert_output_contains "Missing required arguments"
}

@test "ecr_build_push: fails on unknown parameter" {
  run bash "$SCRIPT_UNDER_TEST" --unknown value
  assert_failure
  assert_output_contains "Unknown parameter"
}

@test "ecr_build_push: succeeds with required args" {
  create_mock_aws
  create_mock_docker

  run bash "$SCRIPT_UNDER_TEST" \
    --registry 123456789.dkr.ecr.eu-west-2.amazonaws.com \
    --name my-app \
    --sha a1b2c3d

  assert_success
  assert_output_contains "Successfully built and pushed"
}

@test "ecr_build_push: authenticates to ECR" {
  create_mock_aws
  create_mock_docker

  run bash "$SCRIPT_UNDER_TEST" \
    --registry 123456789.dkr.ecr.eu-west-2.amazonaws.com \
    --name my-app \
    --sha a1b2c3d

  assert_success

  # Check AWS was called for ECR login
  grep -q "aws ecr get-login-password" "$MOCK_CALLS_FILE"
}

@test "ecr_build_push: builds docker image with correct tag" {
  create_mock_aws
  create_mock_docker

  run bash "$SCRIPT_UNDER_TEST" \
    --registry 123456789.dkr.ecr.eu-west-2.amazonaws.com \
    --name my-app \
    --sha a1b2c3d

  assert_success

  # Check docker build was called
  grep -q "docker build" "$MOCK_CALLS_FILE"
  grep -q "my-app:a1b2c3d" "$MOCK_CALLS_FILE"
}

@test "ecr_build_push: pushes docker image" {
  create_mock_aws
  create_mock_docker

  run bash "$SCRIPT_UNDER_TEST" \
    --registry 123456789.dkr.ecr.eu-west-2.amazonaws.com \
    --name my-app \
    --sha a1b2c3d

  assert_success

  # Check docker push was called
  grep -q "docker push" "$MOCK_CALLS_FILE"
}

@test "ecr_build_push: adds version tag when provided" {
  create_mock_aws
  create_mock_docker

  run bash "$SCRIPT_UNDER_TEST" \
    --registry 123456789.dkr.ecr.eu-west-2.amazonaws.com \
    --name my-app \
    --sha a1b2c3d \
    --version 1.0.0

  assert_success
  assert_output_contains "Adding version tag: 1.0.0"

  # Check docker tag was called for version
  grep -q "docker tag" "$MOCK_CALLS_FILE"
}

@test "ecr_build_push: uses custom region when provided" {
  create_mock_aws
  create_mock_docker

  run bash "$SCRIPT_UNDER_TEST" \
    --registry 123456789.dkr.ecr.us-east-1.amazonaws.com \
    --name my-app \
    --sha a1b2c3d \
    --region us-east-1

  assert_success

  # Check AWS was called with custom region
  grep -q "us-east-1" "$MOCK_CALLS_FILE"
}

@test "ecr_build_push: defaults to eu-west-2 region" {
  create_mock_aws
  create_mock_docker

  run bash "$SCRIPT_UNDER_TEST" \
    --registry 123456789.dkr.ecr.eu-west-2.amazonaws.com \
    --name my-app \
    --sha a1b2c3d

  assert_success

  # Check AWS was called with default region
  grep -q "eu-west-2" "$MOCK_CALLS_FILE"
}
