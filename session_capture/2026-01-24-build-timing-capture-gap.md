# Session Capture: Build Timing Capture Gap for Persistent Clusters

**Date**: 2026-01-24
**Session Type**: Discovery / Gap Analysis
**Environment**: All
**Status**: Open - Requires Implementation

## Problem Statement

Build and teardown timings for persistent cluster deployments are **not being captured** in the governance registry.

The `record-build-timing.sh` script writes to `environments/<env>/latest/build_timings.csv` on the `governance-registry` branch. The persistent cluster deployment on `2026-01-24` using Bootstrap v4 was not recorded.

## Root Cause Analysis

### Current State

The `scripts/record-build-timing.sh` script captures build timings with the following schema:

```csv
start_time_utc,end_time_utc,phase,env,build_id,duration_seconds,exit_code,flags,resources_added,resources_changed,resources_destroyed,log_path
```

**Critical Implementation Detail**: The script finds logs by pattern matching:
```bash
find "$REPO_ROOT/$LOG_DIR" -name "*$PHASE*$BUILD_ID*.log"
```

This means both `phase` AND `build_id` must appear in the log filename for timing to be captured.

### Where Timing IS Captured

| Makefile Target | Calls `record-build-timing.sh` | Build Type |
|-----------------|-------------------------------|------------|
| `_phase1-infra` | ✅ Yes (line 278) | Ephemeral |
| `_phase2-bootstrap` | ✅ Yes (line 297) | Ephemeral |

### Where Timing IS NOT Captured

| Makefile Target | Calls `record-build-timing.sh` | Build Type |
|-----------------|-------------------------------|------------|
| `apply-persistent` | ❌ No | Persistent |
| `bootstrap-persistent-v4` (line 995) | ❌ No | Persistent |
| `deploy-persistent` | ❌ No | Persistent |
| `teardown-persistent` | ❌ No | Persistent |

### Why This Happened

The `record-build-timing.sh` script was implemented as part of ADR-0156 for CI build timing capture. The focus was on ephemeral CI-triggered builds. When Bootstrap v4 was later added for persistent clusters, timing capture was not integrated.

## Impact

1. **No visibility** into persistent cluster build/teardown durations
2. **Reliability metrics gap** - can't track SLO for persistent deployments
3. **Cost analysis gap** - can't correlate build time with infrastructure costs
4. **Trend analysis gap** - can't identify performance regressions

## Proposed Fix

### Decision Required: Log Naming Alignment

The script requires log filenames to match pattern `*<phase>*<build_id>*.log`. Current persistent logs don't follow this pattern.

**Current log naming**:
```
bootstrap-v4-dev-goldenpath-dev-eks-20260124T080000Z.log
```

**Required for `build_id=persistent` and `phase=bootstrap-persistent`**:
```
bootstrap-persistent-dev-persistent-20260124T080000Z.log
```

### Option A: Align Log Naming + Add Script Calls (Recommended)

1. **Change log naming** in Makefile to include canonical `build_id` and `phase`:
   ```bash
   log="logs/build-timings/bootstrap-persistent-$(ENV)-persistent-$$(date -u +%Y%m%dT%H%M%SZ).log"
   ```

2. **Add script calls** after each target:
   ```makefile
   @bash scripts/record-build-timing.sh $(ENV) persistent bootstrap-persistent
   ```

### Option B: Add Explicit Log Path to Script (Cleaner, More Work)

Modify `record-build-timing.sh` to accept `--log-path` argument, bypassing pattern matching:
```bash
# New usage:
record-build-timing.sh <env> <build_id> <phase> [--log-path <path>]
```

This decouples timing capture from log filename conventions.

## Files to Modify

| File | Change |
|------|--------|
| `Makefile` | Update log naming in persistent targets, add `record-build-timing.sh` calls |
| `scripts/record-build-timing.sh` | (Option B only) Add `--log-path` argument support |

## Acceptance Criteria

1. [ ] Persistent cluster builds are recorded in `environments/<env>/latest/build_timings.csv` on `governance-registry` branch
2. [ ] Persistent cluster teardowns are recorded in same CSV
3. [ ] Build ID is correctly captured as `persistent`
4. [ ] Duration is accurately calculated
5. [ ] Exit code is captured for success/failure tracking
6. [ ] Log filename matches pattern `*<phase>*<build_id>*.log`

## Related Documentation

- ADR-0156: Platform CI Build Timing Capture
- CL-0128: CI Build Timing Capture
- `scripts/record-build-timing.sh` - The timing capture script (line 47 shows pattern matching)
- PRD-0006: Persistent Cluster Build Timing Capture

## Verification Commands

After implementation:

```bash
# Deploy persistent cluster
make deploy-persistent ENV=dev REGION=eu-west-2 BOOTSTRAP_VERSION=v4

# Verify log was created with correct naming
ls logs/build-timings/ | grep "bootstrap-persistent.*persistent"

# Check governance-registry branch for timing entry
git fetch origin governance-registry
git show origin/governance-registry:environments/development/latest/build_timings.csv | tail -5

# Expected: entry with phase=bootstrap-persistent, build_id=persistent
```

## Priority

**Medium** - Not blocking production, but creates observability gap for platform reliability metrics.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Canonical `build_id` | `persistent` | Distinguishes from ephemeral DD-MM-YY-NN format |
| Phase naming | `bootstrap-persistent`, `teardown-persistent` | Aligns with existing pattern, enables log matching |
| Implementation approach | Option A (align log naming) | Minimal script changes, works with existing infrastructure |

## Notes

- The governance-registry branch stores timing data, not `docs/build-timings.csv`
- Log filename must contain both `phase` and `build_id` for pattern matching
- Consider Option B (explicit log path) for future flexibility
