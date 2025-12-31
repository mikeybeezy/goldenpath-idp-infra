#!/usr/bin/env bash
set -euo pipefail

csv_path="${1:-docs/build-timings.csv}"

if [[ ! -f "${csv_path}" ]]; then
  echo "Missing metrics file: ${csv_path}" >&2
  exit 1
fi

awk -F',' '
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
  if (phase != "build" && phase != "teardown") {
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
  phases[0] = "build"
  phases[1] = "teardown"
  for (i = 0; i < 2; i++) {
    phase = phases[i]
    if (total[phase] > 0) {
      avg = sum[phase] / total[phase]
      printf "%s,%d,%d,%d,%.0f,%d,%d\n", phase, total[phase], ok[phase] + 0, fail[phase] + 0, avg, min[phase], max[phase]
    } else {
      printf "%s,0,0,0,0,0,0\n", phase
    }
  }
}
' "${csv_path}"
