#!/bin/bash
set -e

# Usage: ./generate-build-log.sh <BUILD_ID> <BUILD_DURATION> <BOOTSTRAP_DURATION> <RUN_URL> <OUTCOME> <FLAGS_STRING> [ERROR_MSG]

BUILD_ID="$1"
BUILD_DURATION="$2"
BOOTSTRAP_DURATION="$3"
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
LAST_LOG=$(find "$LOG_DIR" -name "BR-*.md" | sort | tail -n 1)
if [[ -z "$LAST_LOG" ]]; then
  NEXT_SEQ="0001"
else
  LAST_SEQ=$(basename "$LAST_LOG" | cut -d'-' -f2)
  NEXT_SEQ=$(printf "%04d" $((10#$LAST_SEQ + 1)))
fi

LOG_FILE="${LOG_DIR}/BR-${NEXT_SEQ}-${BUILD_ID}.md"

echo "Generating log: ${LOG_FILE}"

# 2. Copy Template
cp "$TEMPLATE" "$LOG_FILE"

# 3. Replace Placeholders
sed -i "s|YYYY-MM-DD|$(date -u +%Y-%m-%d)|g" "$LOG_FILE"
sed -i "s|<build-id>|${BUILD_ID}|g" "$LOG_FILE"
sed -i "s|<branch>|${GITHUB_REF_NAME:-unknown}|g" "$LOG_FILE"
sed -i "s|<sha>|${GITHUB_SHA:-unknown}|g" "$LOG_FILE"
sed -i "s|<url>|${RUN_URL}|g" "$LOG_FILE"
sed -i "s|<script-version>|Automated (See Flags)|g" "$LOG_FILE"
sed -i "s|<flags>|${FLAGS}|g" "$LOG_FILE"
sed -i "s|<build-seconds>|${BUILD_DURATION}|g" "$LOG_FILE"
sed -i "s|<bootstrap-seconds>|${BOOTSTRAP_DURATION}|g" "$LOG_FILE"
sed -i "s|<Outcome>|${OUTCOME}|g" "$LOG_FILE"

# 4. Fill Metrics with defaults
# Plan Delta is hard to capture without grep, default to "See logs"
sed -i "s|<delta>|See logs (Auto-capture pending)|g" "$LOG_FILE"

if [[ -n "$ERROR_MSG" ]]; then
  NOTES="Automated capture: FAILED. Error: ${ERROR_MSG}"
  NOTES=${NOTES//|/-} # Sanitize
else
  NOTES="Automated capture from CI."
fi

sed -i "s|<notes>|${NOTES}|g" "$LOG_FILE"

echo "Log generated successfully."
echo "new_log_path=${LOG_FILE}" >> "$GITHUB_OUTPUT"
