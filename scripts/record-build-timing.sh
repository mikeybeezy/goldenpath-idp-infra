#!/usr/bin/env bash
# SKIP-TDD: Registry script with git branch operations - manual verification only
# Record build timing to governance-registry branch
# ---
# id: SCRIPT-0046
# type: script
# owner: platform-team
# status: active
# maturity: 2
# dry_run:
#   supported: false
#   command_hint: none
# test:
#   runner: bash
#   command: bash tests/scripts/record-build-timing.sh --dry-run
#   evidence: manual
# risk_profile:
#   production_impact: low
#   security_risk: none
#   coupling_risk: low
# ---
# Usage: record-build-timing.sh <env> <build_id> <phase>
# Example: record-build-timing.sh dev 13-01-26-03 terraform-apply

set -euo pipefail

ENV="${1:-}"
BUILD_ID="${2:-}"
PHASE="${3:-}"

if [[ -z "$ENV" || -z "$BUILD_ID" || -z "$PHASE" ]]; then
  echo "Usage: $0 <env> <build_id> <phase>" >&2
  echo "  env: dev|staging|prod" >&2
  echo "  build_id: DD-MM-YY-NN format (e.g., 13-01-26-03)" >&2
  echo "  phase: terraform-apply|bootstrap|teardown" >&2
  exit 1
fi

REGISTRY_BRANCH="${GOVERNANCE_REGISTRY_BRANCH:-governance-registry}"
# Map env alias to full folder name
ENV_FOLDER="$ENV"
[[ "$ENV" == "dev" ]] && ENV_FOLDER="development"
CSV_PATH="environments/$ENV_FOLDER/latest/build_timings.csv"
LOG_DIR="logs/build-timings"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Find the latest log for this phase+build_id
LATEST_LOG=$(find "$REPO_ROOT/$LOG_DIR" -name "*$PHASE*$BUILD_ID*.log" -type f 2>/dev/null | sort -r | head -1)

if [[ -z "$LATEST_LOG" ]]; then
  echo "Warning: No log found for phase=$PHASE, build_id=$BUILD_ID in $LOG_DIR" >&2
  echo "Skipping registry recording." >&2
  exit 0
fi

# Extract timing data
# Try to get start time from log, fallback to file creation time
# Use sed/perl for extracting timestamps instead of grep -oP
START_TIME=$(head -20 "$LATEST_LOG" | grep -E '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z' | head -1 | sed -E 's/.*([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z).*/\1/' || \
             stat -f "%Sm" -t "%Y-%m-%dT%H:%M:%SZ" "$LATEST_LOG" 2>/dev/null || \
             stat -c "%y" "$LATEST_LOG" 2>/dev/null | sed 's/ /T/' | sed 's/\..*/Z/' || \
             date -u +"%Y-%m-%dT%H:%M:%SZ")

END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Calculate duration (handle both GNU and BSD date)
if date --version >/dev/null 2>&1; then
  # GNU date (Linux)
  START_EPOCH=$(date -d "$START_TIME" +%s)
  END_EPOCH=$(date -d "$END_TIME" +%s)
else
  # BSD date (macOS)
  START_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$START_TIME" +%s 2>/dev/null || date +%s)
  END_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$END_TIME" +%s 2>/dev/null || date +%s)
fi
DURATION=$((END_EPOCH - START_EPOCH))

# Try to extract exit code from log
EXIT_CODE=0
if grep -q "Error:" "$LATEST_LOG" || grep -q "FAILED" "$LATEST_LOG"; then
  EXIT_CODE=1
fi

# Extract inventory from terraform output (if terraform-apply phase)
RESOURCES_ADDED=0
RESOURCES_CHANGED=0
RESOURCES_DESTROYED=0

if [[ "$PHASE" == "terraform-apply" ]]; then
  if grep -q "Plan:" "$LATEST_LOG"; then
    # Use sed to extract numbers: "Plan: 17 to add..." -> "17"
    RESOURCES_ADDED=$(grep 'Plan:' "$LATEST_LOG" | tail -1 | sed -E 's/.*Plan: ([0-9]+) to add.*/\1/' || echo "0")
    RESOURCES_CHANGED=$(grep 'Plan:' "$LATEST_LOG" | tail -1 | sed -E 's/.*, ([0-9]+) to change.*/\1/' || echo "0")
    RESOURCES_DESTROYED=$(grep 'Plan:' "$LATEST_LOG" | tail -1 | sed -E 's/.*, ([0-9]+) to destroy.*/\1/' || echo "0")
  fi
  # Also check for "Apply complete!" which shows actual changes
  if grep -q "Apply complete!" "$LATEST_LOG"; then
    # "Apply complete! Resources: 3 added, 1 changed, 0 destroyed."
    APPLY_ADDED=$(grep 'Apply complete!' "$LATEST_LOG" | tail -1 | sed -E 's/.*Resources: ([0-9]+) added.*/\1/' || echo "$RESOURCES_ADDED")
    APPLY_CHANGED=$(grep 'Apply complete!' "$LATEST_LOG" | tail -1 | sed -E 's/.*, ([0-9]+) changed.*/\1/' || echo "$RESOURCES_CHANGED")
    APPLY_DESTROYED=$(grep 'Apply complete!' "$LATEST_LOG" | tail -1 | sed -E 's/.*, ([0-9]+) destroyed.*/\1/' || echo "$RESOURCES_DESTROYED")
    RESOURCES_ADDED=$APPLY_ADDED
    RESOURCES_CHANGED=$APPLY_CHANGED
    RESOURCES_DESTROYED=$APPLY_DESTROYED
  fi
fi

# Relative path for log
LOG_RELATIVE_PATH="${LATEST_LOG#$REPO_ROOT/}"

echo "Recording build timing to governance-registry..."
echo "  Phase: $PHASE"
echo "  Environment: $ENV"
echo "  Build ID: $BUILD_ID"
echo "  Duration: ${DURATION}s"
echo "  Exit Code: $EXIT_CODE"
echo "  Resources: +$RESOURCES_ADDED ~$RESOURCES_CHANGED -$RESOURCES_DESTROYED"
echo "  Log: $LOG_RELATIVE_PATH"

# SKIP FAILURES: If we cannot fetch the branch, warn but do not fail the build.
if ! git fetch origin "$REGISTRY_BRANCH" 2>/dev/null; then
  echo "⚠️  Warning: Cannot fetch $REGISTRY_BRANCH branch. Skipping registry record." >&2
  exit 0
fi

# Save current branch
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Checkout governance-registry
if ! git checkout "$REGISTRY_BRANCH" 2>/dev/null; then
  echo "⚠️  Error: Cannot checkout $REGISTRY_BRANCH branch. Skipping registry record." >&2
  exit 0
fi

# Sync local branch with remote to prevent divergence
# This ensures we're always building on top of the latest remote state
if ! git reset --hard "origin/$REGISTRY_BRANCH" 2>/dev/null; then
  echo "⚠️  Warning: Could not sync with origin/$REGISTRY_BRANCH. Continuing anyway." >&2
fi

# Configure git user for CI environments (GitHub Actions runners don't have this set)
git config user.email "github-actions[bot]@users.noreply.github.com"
git config user.name "github-actions[bot]"

# Ensure CSV directory exists
mkdir -p "$(dirname "$CSV_PATH")"

# Create CSV with header if it doesn't exist
if [[ ! -f "$CSV_PATH" ]]; then
  echo "start_time_utc,end_time_utc,phase,env,build_id,duration_seconds,exit_code,flags,resources_added,resources_changed,resources_destroyed,log_path" > "$CSV_PATH"
fi

# Append record
echo "$START_TIME,$END_TIME,$PHASE,$ENV,$BUILD_ID,$DURATION,$EXIT_CODE,\"\",$RESOURCES_ADDED,$RESOURCES_CHANGED,$RESOURCES_DESTROYED,$LOG_RELATIVE_PATH" >> "$CSV_PATH"

# Commit and push
git add "$CSV_PATH"
git commit -m "chore(registry): record $PHASE for $ENV build $BUILD_ID

Duration: ${DURATION}s
Exit Code: $EXIT_CODE
Resources: +$RESOURCES_ADDED ~$RESOURCES_CHANGED -$RESOURCES_DESTROYED
Log: $LOG_RELATIVE_PATH
" >/dev/null 2>&1 || {
  echo "Warning: Commit failed (maybe no changes)" >&2
}

if git push origin "$REGISTRY_BRANCH" 2>/dev/null; then
  echo "✅ Build timing recorded to governance-registry"
else
  echo "⚠️  Warning: Could not push to $REGISTRY_BRANCH. Commit is local only." >&2
fi

# Return to original branch
git checkout "$ORIGINAL_BRANCH" 2>/dev/null || {
  echo "⚠️  Warning: Could not return to original branch $ORIGINAL_BRANCH" >&2
}

echo "Done."
