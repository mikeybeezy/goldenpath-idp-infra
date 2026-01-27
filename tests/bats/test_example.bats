#!/usr/bin/env bats

# Example bats test file
# Run with: bats tests/bats/

load 'helpers/common'

# Setup runs before each test
setup() {
  export TEST_TEMP_DIR=$(mktemp -d)
}

# Teardown runs after each test
teardown() {
  rm -rf "$TEST_TEMP_DIR"
}

@test "example: true returns success" {
  run true
  assert_success
}

@test "example: false returns failure" {
  run false
  assert_failure
}

@test "example: echo outputs text" {
  run echo "hello world"
  assert_success
  assert_output_contains "hello"
}

@test "example: scripts directory exists" {
  assert_dir_exists "$SCRIPTS_DIR"
}

@test "example: temp directory is created" {
  assert_dir_exists "$TEST_TEMP_DIR"
}

# Example of skipping a test
@test "example: skip if aws not installed" {
  skip_if_command_missing aws
  run aws --version
  assert_success
}
