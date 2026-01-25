#!/usr/bin/env bash
# ---
# id: SCRIPT-0027
# type: script
# owner: platform-team
# status: active
# maturity: 2
# dry_run:
#   supported: true
#   command_hint: --dry-run
# test:
#   runner: shellcheck
#   command: shellcheck scripts/reliability-metrics.sh
#   evidence: declared
# risk_profile:
#   production_impact: low
#   security_risk: low
#   coupling_risk: low
# ---
set -euo pipefail

csv_path="${1:-}"
metrics_env="${METRICS_ENV:-${ENV:-}}"
registry_branch="${GOVERNANCE_REGISTRY_BRANCH:-governance-registry}"
registry_remote="${GOVERNANCE_REGISTRY_REMOTE:-origin}"
tmp_csv=""

if [[ -n "${csv_path}" ]]; then
  if [[ ! -f "${csv_path}" ]]; then
    echo "Missing metrics file: ${csv_path}" >&2
    exit 1
  fi
else
  if [[ -n "${metrics_env}" ]]; then
    env_folder="${metrics_env}"
    [[ "${metrics_env}" == "dev" ]] && env_folder="development"
    csv_path="environments/${env_folder}/latest/build_timings.csv"

    if [[ ! -f "${csv_path}" ]]; then
      if ! command -v git >/dev/null; then
        echo "Missing metrics file: ${csv_path} (git not available to fetch ${registry_remote}/${registry_branch})" >&2
        exit 1
      fi
      tmp_csv="$(mktemp)"
      if git show "${registry_remote}/${registry_branch}:${csv_path}" > "${tmp_csv}" 2>/dev/null; then
        csv_path="${tmp_csv}"
      else
        echo "Missing metrics file: ${csv_path} (not found locally or in ${registry_remote}/${registry_branch})" >&2
        rm -f "${tmp_csv}"
        exit 1
      fi
    fi
  else
    csv_path="docs/build-timings.csv"
    if [[ ! -f "${csv_path}" ]]; then
      echo "Missing metrics file: ${csv_path}" >&2
      exit 1
    fi
  fi
fi

PHASES="${PHASES:-build bootstrap terraform-apply apply-persistent bootstrap-persistent teardown teardown-persistent rds-apply}"

awk -F',' -v phases="${PHASES}" '
BEGIN {
  phase_count = split(phases, phase_list, " ")
  for (i = 1; i <= phase_count; i++) {
    allowed[phase_list[i]] = 1
  }
}
NR==1 {
  for (i = 1; i <= NF; i++) {
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", $i)
    header[$i] = i
  }
  phase_col = header["phase"]
  duration_col = header["duration_seconds"]
  exit_col = header["exit_code"]
  if (!phase_col || !duration_col || !exit_col) {
    print "ERROR: build-timings.csv header missing required columns." > "/dev/stderr"
    exit 2
  }
  next
}
{
  if (NF < exit_col) {
    next
  }
  phase = $phase_col
  if (!(phase in allowed)) {
    next
  }
  duration = $duration_col + 0
  exit_code = $exit_col + 0
  total[phase]++
  sum[phase] += duration
  if (exit_code == 0) {
    ok[phase]++
  } else {
    fail[phase]++
  }
  if (!(phase in min) || duration < min[phase]) {
    min[phase] = duration
  }
  if (!(phase in max) || duration > max[phase]) {
    max[phase] = duration
  }
}
END {
  print "phase,count,success,fail,avg_duration_seconds,min_duration_seconds,max_duration_seconds"
  for (i = 1; i <= phase_count; i++) {
    phase = phase_list[i]
    if (total[phase] > 0) {
      avg = sum[phase] / total[phase]
      printf "%s,%d,%d,%d,%.0f,%d,%d\n", phase, total[phase], ok[phase] + 0, fail[phase] + 0, avg, min[phase], max[phase]
    } else {
      printf "%s,0,0,0,0,0,0\n", phase
    }
  }
}
' "${csv_path}"

if [[ -n "${tmp_csv}" ]]; then
  rm -f "${tmp_csv}"
fi
