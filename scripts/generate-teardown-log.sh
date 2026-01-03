#!/bin/bash
set -e

# Usage: ./generate-teardown-log.sh <BUILD_ID> <DURATION_SECONDS> <RUN_URL> <OUTCOME> <FLAGS_STRING>

BUILD_ID="$1"
DURATION="$2"
RUN_URL="$3"
OUTCOME="$4"
FLAGS="$5"

LOG_DIR="docs/build-run-logs"
TEMPLATE="${LOG_DIR}/TD-TEMPLATE.md"

if [[ -z "$BUILD_ID" ]]; then
  echo "Usage: $0 <BUILD_ID> <DURATION> <URL> <OUTCOME> <FLAGS>"
  exit 1
fi

# 1. Determine next sequence number
# Find max TD-XXXX number
LAST_LOG=$(find "$LOG_DIR" -name "TD-*.md" | sort | tail -n 1)
if [[ -z "$LAST_LOG" ]]; then
  NEXT_SEQ="0001"
else
  # Extract number from TD-XXXX-...
  LAST_SEQ=$(basename "$LAST_LOG" | cut -d'-' -f2)
  # Increment (base 10)
  NEXT_SEQ=$(printf "%04d" $((10#$LAST_SEQ + 1)))
fi

LOG_FILE="${LOG_DIR}/TD-${NEXT_SEQ}-${BUILD_ID}.md"

echo "Generating log: ${LOG_FILE}"

# 2. Copy Template
cp "$TEMPLATE" "$LOG_FILE"

# 3. Replace Placeholders
# Use | as delimiter for sed to avoid escaping / in URLs
sed -i "s|YYYY-MM-DD|$(date -u +%Y-%m-%d)|g" "$LOG_FILE"
sed -i "s|<build-id>|${BUILD_ID}|g" "$LOG_FILE"
sed -i "s|<branch>|${GITHUB_REF_NAME:-unknown}|g" "$LOG_FILE"
sed -i "s|<sha>|${GITHUB_SHA:-unknown}|g" "$LOG_FILE"
sed -i "s|<url>|${RUN_URL}|g" "$LOG_FILE"
sed -i "s|<script-version>|v2 (automated)|g" "$LOG_FILE"
sed -i "s|<flags>|${FLAGS}|g" "$LOG_FILE"
sed -i "s|<seconds>|${DURATION}|g" "$LOG_FILE"
sed -i "s|<Outcome>|${OUTCOME}|g" "$LOG_FILE"

# 4. Fill Metrics Placeholders with '0' (Automation defaults to 0, human can update if needed)
# Or ideally, we grep the teardown output? For now, set to "?" to prompt review, or "0" if we trust the clean teardown.
# Let's use "0 (auto)" to be safe.
sed -i "s|<count>|0 (auto)|g" "$LOG_FILE"
sed -i "s|<notes>|Automated capture from CI.|g" "$LOG_FILE"
sed -i "s|<finding>|N/A|g" "$LOG_FILE"
sed -i "s|<impact>|N/A|g" "$LOG_FILE"
sed -i "s|<action>|N/A|g" "$LOG_FILE"

echo "Log generated successfully."
echo "new_log_path=${LOG_FILE}" >> "$GITHUB_OUTPUT"
