#!/bin/bash
set -e

# Usage: ./generate-teardown-log.sh <BUILD_ID> <DURATION_SECONDS> <RUN_URL> <OUTCOME> <FLAGS_STRING> [ERROR_MSG]

BUILD_ID="$1"
DURATION="$2"
RUN_URL="$3"
OUTCOME="$4"
FLAGS="$5"
ERROR_MSG="$6"

LOG_DIR="docs/build-run-logs"
TEMPLATE="${LOG_DIR}/TD-TEMPLATE.md"

if [[ -z "$BUILD_ID" ]]; then
  echo "Usage: $0 <BUILD_ID> <DURATION> <URL> <OUTCOME> <FLAGS> [ERROR_MSG]"
  exit 1
fi

# 1. Determine next sequence number
# Find max TD-XXXX number
LAST_LOG=$(find "$LOG_DIR" -name "TD-*.md" ! -name "TD-TEMPLATE.md" | sort | tail -n 1)
if [[ -z "$LAST_LOG" ]]; then
  NEXT_SEQ="0001"
else
  # Extract number from TD-XXXX-...
  LAST_SEQ=$(basename "$LAST_LOG" | cut -d'-' -f2)
  # Increment (base 10)
  NEXT_SEQ=$(printf "%04d" $((10#$LAST_SEQ + 1)))
fi

RUN_ID="TD-${NEXT_SEQ}"
LOG_FILE="${LOG_DIR}/${RUN_ID}-${BUILD_ID}.md"

echo "Generating log: ${LOG_FILE}"

# 2. Copy Template
cp "$TEMPLATE" "$LOG_FILE"

# 3. Replace Placeholders (portable across macOS/Linux)
SAFE_FLAGS="${FLAGS//|/-}"
if [[ -n "$ERROR_MSG" ]]; then
  NOTES="Automated capture: FAILED. Error: ${ERROR_MSG}"
  NOTES=${NOTES//|/-}
else
  NOTES="Automated capture from CI."
fi

DATE_UTC="$(date -u +%Y-%m-%d)" \
RUN_ID="${RUN_ID}" \
BUILD_ID="${BUILD_ID}" \
BRANCH_NAME="${GITHUB_REF_NAME:-unknown}" \
COMMIT_SHA="${GITHUB_SHA:-unknown}" \
RUN_URL="${RUN_URL}" \
SAFE_FLAGS="${SAFE_FLAGS}" \
DURATION="${DURATION}" \
OUTCOME="${OUTCOME}" \
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
    "<url>": os.environ["RUN_URL"],
    "<script-version>": "Automated (See Flags)",
    "<flags>": os.environ["SAFE_FLAGS"],
    "<seconds>": os.environ["DURATION"],
    "<Outcome>": os.environ["OUTCOME"],
    "<count>": "0 (auto)",
    "<finding>": "N/A",
    "<impact>": "N/A",
    "<action>": "N/A",
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
