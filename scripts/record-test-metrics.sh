#!/usr/bin/env bash
# Record test metrics JSON to governance-registry branch
# ---
# id: SCRIPT-0061
# type: script
# owner: platform-team
# status: active
# maturity: 1
# dry_run:
#   supported: false
#   command_hint: none
# test:
#   runner: bash
#   command: bash scripts/record-test-metrics.sh dev /tmp/test-metrics.json
#   evidence: manual
# risk_profile:
#   production_impact: low
#   security_risk: none
#   coupling_risk: low
# ---
# Usage: record-test-metrics.sh <env> <metrics_json_path>
# Example: record-test-metrics.sh dev test-results/test-metrics.json

set -euo pipefail

ENV="${1:-}"
METRICS_PATH="${2:-}"

if [[ -z "$ENV" || -z "$METRICS_PATH" ]]; then
  echo "Usage: $0 <env> <metrics_json_path>" >&2
  echo "  env: dev|staging|prod" >&2
  exit 1
fi

if [[ ! -f "$METRICS_PATH" ]]; then
  echo "Warning: metrics JSON not found at $METRICS_PATH. Skipping registry record." >&2
  exit 0
fi

REGISTRY_BRANCH="${GOVERNANCE_REGISTRY_BRANCH:-governance-registry}"
ENV_FOLDER="$ENV"
[[ "$ENV" == "dev" ]] && ENV_FOLDER="development"

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ABS_METRICS_PATH="$(cd "$REPO_ROOT" && realpath "$METRICS_PATH")"
TMP_METRICS="$(mktemp)"
cp "$ABS_METRICS_PATH" "$TMP_METRICS"
TMP_MERGED="$(mktemp)"

COMMIT_SHA="$(python3 - "$TMP_METRICS" <<'PY'
import json, sys
path = sys.argv[1]
try:
    data = json.load(open(path, "r", encoding="utf-8"))
    print(data.get("commit", "unknown"))
except Exception:
    print("unknown")
PY
)"
SHORT_SHA="${COMMIT_SHA:0:7}"
TS="$(date -u +%Y-%m-%d-%H%MZ)"

LATEST_PATH="environments/$ENV_FOLDER/latest/test_metrics.json"
HIST_DIR="environments/$ENV_FOLDER/history/${TS}-${SHORT_SHA}"

echo "Recording test metrics to governance-registry..."
echo "  Environment: $ENV"
echo "  Metrics: $METRICS_PATH"
echo "  Commit: $COMMIT_SHA"

if ! git fetch origin "$REGISTRY_BRANCH" 2>/dev/null; then
  echo "⚠️  Warning: Cannot fetch $REGISTRY_BRANCH branch. Skipping registry record." >&2
  exit 0
fi

ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if ! git checkout "$REGISTRY_BRANCH" 2>/dev/null; then
  echo "⚠️  Error: Cannot checkout $REGISTRY_BRANCH branch. Skipping registry record." >&2
  git checkout "$ORIGINAL_BRANCH" 2>/dev/null || true
  exit 0
fi

# Sync local branch with remote to prevent divergence
# This ensures we're always building on top of the latest remote state
if ! git reset --hard "origin/$REGISTRY_BRANCH" 2>/dev/null; then
  echo "⚠️  Warning: Could not sync with origin/$REGISTRY_BRANCH. Continuing anyway." >&2
fi

mkdir -p "$(dirname "$LATEST_PATH")" "$HIST_DIR"

# Merge with existing latest metrics if present (preserve other frameworks)
if [[ -f "$LATEST_PATH" ]]; then
  python3 - "$LATEST_PATH" "$TMP_METRICS" "$TMP_MERGED" <<'PY'
import json
import sys

existing_path, new_path, out_path = sys.argv[1:4]

def load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

existing = load(existing_path)
new = load(new_path)

merged = dict(existing) if isinstance(existing, dict) else {}
if not merged:
    merged = dict(new) if isinstance(new, dict) else {}

existing_fw = {f.get("framework"): f for f in merged.get("frameworks", []) if isinstance(f, dict)}
new_fw = {f.get("framework"): f for f in new.get("frameworks", []) if isinstance(f, dict)}
existing_fw.update(new_fw)
frameworks = [v for v in existing_fw.values() if v]
frameworks.sort(key=lambda x: x.get("framework", ""))

merged["repo"] = new.get("repo", merged.get("repo"))
merged["branch"] = new.get("branch", merged.get("branch"))
merged["commit"] = new.get("commit", merged.get("commit"))
merged["ci_run_id"] = new.get("ci_run_id", merged.get("ci_run_id"))
merged["last_run"] = new.get("last_run", merged.get("last_run"))
merged["frameworks"] = frameworks

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(merged, f, indent=2)
PY
  cp "$TMP_MERGED" "$LATEST_PATH"
  cp "$TMP_MERGED" "$HIST_DIR/test_metrics.json"
else
  cp "$TMP_METRICS" "$LATEST_PATH"
  cp "$TMP_METRICS" "$HIST_DIR/test_metrics.json"
fi

git add "$LATEST_PATH" "$HIST_DIR/test_metrics.json"
git commit -m "chore(registry): record test metrics for $ENV @ ${SHORT_SHA}" >/dev/null 2>&1 || {
  echo "Warning: Commit failed (maybe no changes)" >&2
}

if git push origin "$REGISTRY_BRANCH" 2>/dev/null; then
  echo "✅ Test metrics recorded to governance-registry"
else
  echo "⚠️  Warning: Could not push to $REGISTRY_BRANCH. Commit is local only." >&2
fi

git checkout "$ORIGINAL_BRANCH" 2>/dev/null || {
  echo "⚠️  Warning: Could not return to original branch $ORIGINAL_BRANCH" >&2
}

rm -f "$TMP_METRICS" "$TMP_MERGED"
echo "Done."
