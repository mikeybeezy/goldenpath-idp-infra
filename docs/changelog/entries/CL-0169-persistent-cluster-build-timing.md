---
id: CL-0169
title: Persistent Cluster Build Timing Capture
type: changelog
date: 2026-01-24
author: platform-team
breaking_change: false
---

## Summary

Enabled build timing capture for persistent cluster deployments via `record-build-timing.sh`.

## Changes

### Log Naming Alignment

Updated log filenames in Makefile to match the pattern `*<phase>*<build_id>*.log` required by `record-build-timing.sh`:

| Target | Old Log Name | New Log Name |
|--------|-------------|--------------|
| `bootstrap-persistent` | `bootstrap-persistent-<env>-<cluster>-<ts>.log` | `bootstrap-persistent-<env>-persistent-<ts>.log` |
| `bootstrap-persistent-v4` | `bootstrap-v4-<env>-<cluster>-<ts>.log` | `bootstrap-persistent-<env>-persistent-<ts>.log` |
| `teardown-persistent` | `teardown-persistent-<env>-<cluster>-<ts>.log` | `teardown-persistent-<env>-persistent-<ts>.log` |

### Timing Capture Integration

Added `record-build-timing.sh` calls to persistent cluster targets:

- `bootstrap-persistent`: Records timing after v1-v3 bootstrap completes
- `bootstrap-persistent-v4`: Records timing after v4 bootstrap completes
- `teardown-persistent`: Records timing after teardown completes

All calls use `|| true` to ensure timing capture failures don't block builds (fail-open).

### Build ID Convention

- Persistent clusters use `persistent` as the canonical `build_id`
- Distinguishes from ephemeral builds which use `DD-MM-YY-NN` format
- Enables filtering and aggregation in governance registry CSV

## Impact

- Non-breaking change
- Timing data now recorded to `environments/<env>/latest/build_timings.csv` on governance-registry branch
- Enables reliability metrics and trend analysis for persistent clusters
- Closes observability gap identified in PRD-0006

## Related

- PRD-0006: Persistent Cluster Build Timing Capture
- ADR-0156: Platform CI Build Timing Capture
- Session Capture: 2026-01-24-build-timing-capture-gap.md
