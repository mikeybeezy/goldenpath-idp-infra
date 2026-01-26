#!/usr/bin/env bats
# Tests for bootstrap/00_prereqs/00_check_tools.sh
# SCRIPT-0001: Prerequisite tool checker
#
# Run with: bats tests/bats/test_check_tools.bats

load 'helpers/common'

SCRIPT_UNDER_TEST="${PROJECT_ROOT}/bootstrap/00_prereqs/00_check_tools.sh"

setup() {
  export TEST_TEMP_DIR=$(mktemp -d)
  export PATH="${TEST_TEMP_DIR}/bin:$PATH"
  mkdir -p "${TEST_TEMP_DIR}/bin"
}

teardown() {
  rm -rf "$TEST_TEMP_DIR"
}

# Helper: Create a mock command that succeeds
create_mock_tool() {
  local name="$1"
  local version_output="$2"
  cat > "${TEST_TEMP_DIR}/bin/${name}" << EOF
#!/bin/bash
if [[ "\$1" == "--version" ]] || [[ "\$1" == "version" ]]; then
  echo "${version_output}"
fi
exit 0
EOF
  chmod +x "${TEST_TEMP_DIR}/bin/${name}"
}

@test "check_tools: script file exists" {
  assert_file_exists "$SCRIPT_UNDER_TEST"
}

@test "check_tools: script is executable" {
  [[ -x "$SCRIPT_UNDER_TEST" ]]
}

@test "check_tools: passes when all tools present" {
  # Create mock tools
  create_mock_tool "aws" "aws-cli/2.15.0 Python/3.11.6"
  create_mock_tool "kubectl" "Client Version: v1.29.0"
  create_mock_tool "helm" "version.BuildInfo{Version:\"v3.14.0\"}"

  run bash "$SCRIPT_UNDER_TEST"
  assert_success
}

@test "check_tools: fails when aws missing" {
  # Create only kubectl and helm, not aws
  create_mock_tool "kubectl" "Client Version: v1.29.0"
  create_mock_tool "helm" "version.BuildInfo{Version:\"v3.14.0\"}"

  # Remove aws from PATH if it exists
  export PATH="${TEST_TEMP_DIR}/bin"

  run bash "$SCRIPT_UNDER_TEST"
  assert_failure
  assert_output_contains "Missing required tool: aws"
}

@test "check_tools: fails when kubectl missing" {
  create_mock_tool "aws" "aws-cli/2.15.0"
  create_mock_tool "helm" "version.BuildInfo{Version:\"v3.14.0\"}"

  export PATH="${TEST_TEMP_DIR}/bin"

  run bash "$SCRIPT_UNDER_TEST"
  assert_failure
  assert_output_contains "Missing required tool: kubectl"
}

@test "check_tools: fails when helm missing" {
  create_mock_tool "aws" "aws-cli/2.15.0"
  create_mock_tool "kubectl" "Client Version: v1.29.0"

  export PATH="${TEST_TEMP_DIR}/bin"

  run bash "$SCRIPT_UNDER_TEST"
  assert_failure
  assert_output_contains "Missing required tool: helm"
}

@test "check_tools: prints version output for audit" {
  create_mock_tool "aws" "aws-cli/2.15.0 Python/3.11.6"
  create_mock_tool "kubectl" "Client Version: v1.29.0"
  create_mock_tool "helm" "version.BuildInfo{Version:\"v3.14.0\"}"

  run bash "$SCRIPT_UNDER_TEST"
  assert_success
  # Verify version output is printed
  assert_output_contains "aws-cli"
  assert_output_contains "Client Version"
}
