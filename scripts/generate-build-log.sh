#!/bin/bash
set -e

# Usage: ./generate-build-log.sh <BUILD_ID> <BUILD_DURATION> <BOOTSTRAP_DURATION> <RUN_URL> <OUTCOME> <FLAGS_STRING> [ERROR_MSG]

BUILD_ID="$1"
BUILD_DURATION="${2:-"-"}"
BOOTSTRAP_DURATION="${3:-"-"}"
RUN_URL="$4"
OUTCOME="$5"
FLAGS="$6"
ERROR_MSG="$7"

LOG_DIR="docs/build-run-logs"
TEMPLATE="${LOG_DIR}/BR-TEMPLATE.md"

if [[ -z "$BUILD_ID" ]]; then
  echo "Usage: $0 <BUILD_ID> <BUILD_DURATION> <BOOTSTRAP_DURATION> <URL> <OUTCOME> <FLAGS> [ERROR_MSG]"
  exit 1
fi

# 1. Determine next sequence number
# Find max BR-XXXX number
LAST_LOG=$(find "$LOG_DIR" -name "BR-*.md" ! -name "BR-TEMPLATE.md" | sort | tail -n 1)
if [[ -z "$LAST_LOG" ]]; then
  NEXT_SEQ="0001"
else
  LAST_SEQ=$(basename "$LAST_LOG" | cut -d'-' -f2)
  NEXT_SEQ=$(printf "%04d" $((10#$LAST_SEQ + 1)))
fi

RUN_ID="BR-${NEXT_SEQ}"
LOG_FILE="${LOG_DIR}/${RUN_ID}-${BUILD_ID}.md"

echo "Generating log: ${LOG_FILE}"

# 2. Copy Template
cp "$TEMPLATE" "$LOG_FILE"

WORKFLOW_NAME="${GITHUB_WORKFLOW:-CI Bootstrap}"
JOB_LIST="See workflow run"
CONFIG_SOURCE="See workflow run"
STORAGE_ADDONS="See workflow run"
IRSA_STRATEGY="See workflow run"
PLAN_DELTA="See logs (Auto-capture pending)"
TEARDOWN_DURATION="-"
ARTIFACTS="See workflow run"
SAFE_FLAGS="${FLAGS//|/-}"

# 3. Replace Placeholders (portable across macOS/Linux)
if [[ -n "$ERROR_MSG" ]]; then
  NOTES="Automated capture: FAILED. Error: ${ERROR_MSG}"
  NOTES=${NOTES//|/-} # Sanitize
else
  NOTES="Automated capture from CI."
fi

DATE_UTC="$(date -u +%Y-%m-%d)" \
RUN_ID="${RUN_ID}" \
BUILD_ID="${BUILD_ID}" \
BRANCH_NAME="${GITHUB_REF_NAME:-unknown}" \
COMMIT_SHA="${GITHUB_SHA:-unknown}" \
WORKFLOW_NAME="${WORKFLOW_NAME}" \
JOB_LIST="${JOB_LIST}" \
RUN_URL="${RUN_URL}" \
CONFIG_SOURCE="${CONFIG_SOURCE}" \
STORAGE_ADDONS="${STORAGE_ADDONS}" \
IRSA_STRATEGY="${IRSA_STRATEGY}" \
PLAN_DELTA="${PLAN_DELTA}" \
BUILD_DURATION="${BUILD_DURATION}" \
BOOTSTRAP_DURATION="${BOOTSTRAP_DURATION}" \
TEARDOWN_DURATION="${TEARDOWN_DURATION}" \
OUTCOME="${OUTCOME}" \
ARTIFACTS="${ARTIFACTS}" \
SAFE_FLAGS="${SAFE_FLAGS}" \
NOTES="${NOTES}" \
LOG_FILE="${LOG_FILE}" \
python - <<'PY'
import os
from pathlib import Path

path = Path(os.environ["LOG_FILE"])
content = path.read_text()

repls = {
    "YYYY-MM-DD": os.environ["DATE_UTC"],
    "<run-id>": os.environ["RUN_ID"],
    "<build-id>": os.environ["BUILD_ID"],
    "<branch>": os.environ["BRANCH_NAME"],
    "<sha>": os.environ["COMMIT_SHA"],
    "<workflow-name>": os.environ["WORKFLOW_NAME"],
    "<job-list>": os.environ["JOB_LIST"],
    "<url>": os.environ["RUN_URL"],
    "<config-source>": os.environ["CONFIG_SOURCE"],
    "<storage-addons>": os.environ["STORAGE_ADDONS"],
    "<irsa-strategy>": os.environ["IRSA_STRATEGY"],
    "<plan-delta>": os.environ["PLAN_DELTA"],
    "<build-seconds>": os.environ["BUILD_DURATION"],
    "<bootstrap-seconds>": os.environ["BOOTSTRAP_DURATION"],
    "<teardown-seconds>": os.environ["TEARDOWN_DURATION"],
    "<Outcome>": os.environ["OUTCOME"],
    "<artifacts>": os.environ["ARTIFACTS"],
    "<flags>": os.environ["SAFE_FLAGS"],
    "<notes>": os.environ["NOTES"],
}

for key, value in repls.items():
    content = content.replace(key, value)

path.write_text(content)
PY

echo "Log generated successfully."
if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  echo "new_log_path=${LOG_FILE}" >> "$GITHUB_OUTPUT"
fi
