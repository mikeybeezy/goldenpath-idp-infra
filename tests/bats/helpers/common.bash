# Common helper functions for bats tests
# Source this file in your .bats tests: load 'helpers/common'

# Project root directory
export PROJECT_ROOT="${BATS_TEST_DIRNAME}/../.."

# Scripts directory
export SCRIPTS_DIR="${PROJECT_ROOT}/scripts"

# Setup function - runs before each test
setup() {
  # Create temp directory for test artifacts
  export TEST_TEMP_DIR=$(mktemp -d)
}

# Teardown function - runs after each test
teardown() {
  # Clean up temp directory
  if [[ -d "$TEST_TEMP_DIR" ]]; then
    rm -rf "$TEST_TEMP_DIR"
  fi
}

# Assert file exists
assert_file_exists() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    echo "Expected file to exist: $file" >&2
    return 1
  fi
}

# Assert file does not exist
assert_file_not_exists() {
  local file="$1"
  if [[ -f "$file" ]]; then
    echo "Expected file to not exist: $file" >&2
    return 1
  fi
}

# Assert directory exists
assert_dir_exists() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    echo "Expected directory to exist: $dir" >&2
    return 1
  fi
}

# Assert string contains substring
assert_contains() {
  local haystack="$1"
  local needle="$2"
  if [[ "$haystack" != *"$needle"* ]]; then
    echo "Expected '$haystack' to contain '$needle'" >&2
    return 1
  fi
}

# Assert string equals
assert_equals() {
  local expected="$1"
  local actual="$2"
  if [[ "$expected" != "$actual" ]]; then
    echo "Expected: '$expected'" >&2
    echo "Actual:   '$actual'" >&2
    return 1
  fi
}

# Assert command succeeds
assert_success() {
  if [[ "$status" -ne 0 ]]; then
    echo "Expected command to succeed, but it failed with status $status" >&2
    echo "Output: $output" >&2
    return 1
  fi
}

# Assert command fails
assert_failure() {
  if [[ "$status" -eq 0 ]]; then
    echo "Expected command to fail, but it succeeded" >&2
    echo "Output: $output" >&2
    return 1
  fi
}

# Assert output contains string
assert_output_contains() {
  local needle="$1"
  if [[ "$output" != *"$needle"* ]]; then
    echo "Expected output to contain: '$needle'" >&2
    echo "Actual output: '$output'" >&2
    return 1
  fi
}

# Skip test if command not available
skip_if_command_missing() {
  local cmd="$1"
  if ! command -v "$cmd" &> /dev/null; then
    skip "$cmd is not installed"
  fi
}

# Skip test if environment variable not set
skip_if_env_missing() {
  local var="$1"
  if [[ -z "${!var}" ]]; then
    skip "Environment variable $var is not set"
  fi
}

# Mock a command by creating a function
mock_command() {
  local cmd="$1"
  local output="$2"
  local exit_code="${3:-0}"

  eval "$cmd() { echo '$output'; return $exit_code; }"
  export -f "$cmd"
}
