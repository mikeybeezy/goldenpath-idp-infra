#!/bin/bash
# ---
# id: SCRIPT-0015
# type: script
# owner: platform-team
# status: active
# maturity: 2
# dry_run:
#   supported: true
#   command_hint: --dry-run
# test:
#   runner: shellcheck
#   command: shellcheck scripts/generate-teardown-log.sh
#   evidence: declared
# risk_profile:
#   production_impact: low
#   security_risk: low
#   coupling_risk: low
# ---
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

LOG_FILE="${LOG_DIR}/TD-${NEXT_SEQ}-${BUILD_ID}.md"

echo "Generating log: ${LOG_FILE}"

# 2. Copy Template
cp "$TEMPLATE" "$LOG_FILE"

# 3. Replace Placeholders
# Use | as delimiter for sed to avoid escaping / in URLs
SAFE_FLAGS="${FLAGS//|/-}"
sed -i "s|YYYY-MM-DD|$(date -u +%Y-%m-%d)|g" "$LOG_FILE"
sed -i "s|<build-id>|${BUILD_ID}|g" "$LOG_FILE"
sed -i "s|<branch>|${GITHUB_REF_NAME:-unknown}|g" "$LOG_FILE"
sed -i "s|<sha>|${GITHUB_SHA:-unknown}|g" "$LOG_FILE"
sed -i "s|<url>|${RUN_URL}|g" "$LOG_FILE"
sed -i "s|<script-version>|Automated (See Flags)|g" "$LOG_FILE"
sed -i "s|<flags>|${SAFE_FLAGS}|g" "$LOG_FILE"
sed -i "s|<seconds>|${DURATION}|g" "$LOG_FILE"
sed -i "s|<Outcome>|${OUTCOME}|g" "$LOG_FILE"

# 4. Fill Metrics Placeholders with '0' (Automation defaults to '0 (auto)')
sed -i "s|<count>|0 (auto)|g" "$LOG_FILE"
sed -i "s|<finding>|N/A|g" "$LOG_FILE"
sed -i "s|<impact>|N/A|g" "$LOG_FILE"
sed -i "s|<action>|N/A|g" "$LOG_FILE"

if [[ -n "$ERROR_MSG" ]]; then
  NOTES="Automated capture: FAILED. Error: ${ERROR_MSG}"
  # Escape newlines or special chars for sed if necessary, but keep simple for now
  # Replace | with - to avoid sed delimiter conflict
  NOTES=${NOTES//|/-}
else
  NOTES="Automated capture from CI."
fi

sed -i "s|<notes>|${NOTES}|g" "$LOG_FILE"

echo "Log generated successfully."
echo "new_log_path=${LOG_FILE}" >> "$GITHUB_OUTPUT"
