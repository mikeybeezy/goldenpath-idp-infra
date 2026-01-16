#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# VALIDATION TEST: Teardown V3 Script
# =============================================================================
#
# Purpose: Validate syntax, structure, and required functions in teardown v3
#
# Usage:
#   ./tests/scripts/teardown-v3/validate-teardown-v3.sh
#
# Output:
#   - Test results to stdout
#   - Exit code 0 on success, 1 on failure
#
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
TEARDOWN_V3="${REPO_ROOT}/bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v3.sh"
CLEANUP_ORPHANS="${REPO_ROOT}/bootstrap/60_tear_down_clean_up/cleanup-orphans.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
SKIPPED=0

log_test() {
  local name="$1"
  local status="$2"
  local message="${3:-}"

  case "${status}" in
    PASS)
      echo -e "${GREEN}[PASS]${NC} ${name}"
      PASSED=$((PASSED + 1))
      ;;
    FAIL)
      echo -e "${RED}[FAIL]${NC} ${name}: ${message}"
      FAILED=$((FAILED + 1))
      ;;
    SKIP)
      echo -e "${YELLOW}[SKIP]${NC} ${name}: ${message}"
      SKIPPED=$((SKIPPED + 1))
      ;;
  esac
}

# =============================================================================
# TEST: Script exists
# =============================================================================

test_script_exists() {
  if [[ -f "${TEARDOWN_V3}" ]]; then
    log_test "teardown-v3.sh exists" "PASS"
  else
    log_test "teardown-v3.sh exists" "FAIL" "File not found: ${TEARDOWN_V3}"
  fi

  if [[ -f "${CLEANUP_ORPHANS}" ]]; then
    log_test "cleanup-orphans.sh exists" "PASS"
  else
    log_test "cleanup-orphans.sh exists" "FAIL" "File not found: ${CLEANUP_ORPHANS}"
  fi
}

# =============================================================================
# TEST: Syntax validation (bash -n)
# =============================================================================

test_syntax() {
  if bash -n "${TEARDOWN_V3}" 2>/dev/null; then
    log_test "teardown-v3.sh syntax" "PASS"
  else
    log_test "teardown-v3.sh syntax" "FAIL" "Syntax errors detected"
  fi

  if bash -n "${CLEANUP_ORPHANS}" 2>/dev/null; then
    log_test "cleanup-orphans.sh syntax" "PASS"
  else
    log_test "cleanup-orphans.sh syntax" "FAIL" "Syntax errors detected"
  fi
}

# =============================================================================
# TEST: Required functions exist
# =============================================================================

test_required_functions() {
  local required_functions=(
    "log_step"
    "log_info"
    "log_warn"
    "log_error"
    "log_breakglass"
    "stage_banner"
    "stage_done"
    "delete_nodegroups_via_aws"
    "wait_for_nodegroup_deletion"
    "delete_rds_instances_for_build"
    "delete_lbs_by_cluster_tag"
    "delete_target_groups_for_cluster"
    "wait_for_lb_enis"
  )

  for func in "${required_functions[@]}"; do
    if grep -q "^${func}()" "${TEARDOWN_V3}" 2>/dev/null; then
      log_test "Function ${func}() defined" "PASS"
    else
      log_test "Function ${func}() defined" "FAIL" "Not found in teardown-v3.sh"
    fi
  done
}

# =============================================================================
# TEST: Stage structure (8 stages)
# =============================================================================

test_stage_structure() {
  local expected_stages=(
    "STAGE 1"
    "STAGE 2"
    "STAGE 3"
    "STAGE 4"
    "STAGE 5"
    "STAGE 6"
    "STAGE 7"
    "STAGE 8"
  )

  for stage in "${expected_stages[@]}"; do
    if grep -q "${stage}" "${TEARDOWN_V3}" 2>/dev/null; then
      log_test "${stage} present" "PASS"
    else
      log_test "${stage} present" "FAIL" "Not found in script"
    fi
  done
}

# =============================================================================
# TEST: No UNKNOWN STEP patterns
# =============================================================================

test_no_unknown_steps() {
  if grep -qi "unknown.step" "${TEARDOWN_V3}" 2>/dev/null; then
    log_test "No UNKNOWN STEP patterns" "FAIL" "Found unknown step patterns"
  else
    log_test "No UNKNOWN STEP patterns" "PASS"
  fi
}

# =============================================================================
# TEST: RDS cleanup support
# =============================================================================

test_rds_support() {
  if grep -q "DELETE_RDS_INSTANCES" "${TEARDOWN_V3}" 2>/dev/null; then
    log_test "RDS cleanup variable defined" "PASS"
  else
    log_test "RDS cleanup variable defined" "FAIL" "DELETE_RDS_INSTANCES not found"
  fi

  if grep -q "rds:db" "${CLEANUP_ORPHANS}" 2>/dev/null; then
    log_test "RDS cleanup in orphan script" "PASS"
  else
    log_test "RDS cleanup in orphan script" "FAIL" "RDS support not found"
  fi
}

# =============================================================================
# TEST: Nodegroup wait logic
# =============================================================================

test_nodegroup_wait() {
  if grep -q "wait_for_nodegroup_deletion" "${TEARDOWN_V3}" 2>/dev/null; then
    log_test "Nodegroup wait function called" "PASS"
  else
    log_test "Nodegroup wait function called" "FAIL" "Function not invoked"
  fi

  if grep -q "NODEGROUP_WAIT_TIMEOUT\|NODEGROUP_DELETE_TIMEOUT" "${TEARDOWN_V3}" 2>/dev/null; then
    log_test "Nodegroup timeout configurable" "PASS"
  else
    log_test "Nodegroup timeout configurable" "FAIL" "Timeout variable not found"
  fi
}

# =============================================================================
# TEST: Break-glass logging
# =============================================================================

test_breakglass_logging() {
  if grep -q "BREAK-GLASS" "${TEARDOWN_V3}" 2>/dev/null; then
    log_test "Break-glass logging present" "PASS"
  else
    log_test "Break-glass logging present" "FAIL" "No BREAK-GLASS labels found"
  fi
}

# =============================================================================
# TEST: Orphan cleanup v2.x.x features
# =============================================================================

test_orphan_cleanup_v2() {
  if grep -qE "Version: 2\.[0-9]+\.[0-9]+" "${CLEANUP_ORPHANS}" 2>/dev/null; then
    log_test "Orphan cleanup version 2.x.x" "PASS"
  else
    log_test "Orphan cleanup version 2.x.x" "FAIL" "Version 2.x.x header not found"
  fi

  if grep -q "nodegroup_wait_timeout" "${CLEANUP_ORPHANS}" 2>/dev/null; then
    log_test "Orphan cleanup nodegroup wait" "PASS"
  else
    log_test "Orphan cleanup nodegroup wait" "FAIL" "nodegroup_wait_timeout not found"
  fi
}

# =============================================================================
# TEST: Shellcheck (if available)
# =============================================================================

test_shellcheck() {
  if command -v shellcheck >/dev/null 2>&1; then
    if shellcheck -S warning "${TEARDOWN_V3}" 2>/dev/null; then
      log_test "Shellcheck teardown-v3.sh" "PASS"
    else
      log_test "Shellcheck teardown-v3.sh" "FAIL" "Shellcheck warnings/errors"
    fi

    if shellcheck -S warning "${CLEANUP_ORPHANS}" 2>/dev/null; then
      log_test "Shellcheck cleanup-orphans.sh" "PASS"
    else
      log_test "Shellcheck cleanup-orphans.sh" "FAIL" "Shellcheck warnings/errors"
    fi
  else
    log_test "Shellcheck" "SKIP" "shellcheck not installed"
  fi
}

# =============================================================================
# MAIN
# =============================================================================

echo "============================================================================="
echo "VALIDATION TEST: Teardown V3 Script"
echo "============================================================================="
echo "Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "Teardown Script: ${TEARDOWN_V3}"
echo "Cleanup Script: ${CLEANUP_ORPHANS}"
echo "============================================================================="
echo ""

test_script_exists
test_syntax
test_required_functions
test_stage_structure
test_no_unknown_steps
test_rds_support
test_nodegroup_wait
test_breakglass_logging
test_orphan_cleanup_v2
test_shellcheck

echo ""
echo "============================================================================="
echo "TEST RESULTS"
echo "============================================================================="
echo -e "Passed: ${GREEN}${PASSED}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"
echo -e "Skipped: ${YELLOW}${SKIPPED}${NC}"
echo "============================================================================="

if [[ "${FAILED}" -gt 0 ]]; then
  echo -e "${RED}VALIDATION FAILED${NC}"
  exit 1
else
  echo -e "${GREEN}VALIDATION PASSED${NC}"
  exit 0
fi
