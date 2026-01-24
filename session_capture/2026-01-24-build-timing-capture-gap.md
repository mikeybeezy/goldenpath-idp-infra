# Session Capture: Build Timing Capture Gap for Persistent Clusters

**Date**: 2026-01-24
**Session Type**: Discovery / Gap Analysis
**Environment**: All
**Status**: Open - Requires Implementation

## Problem Statement

Build and teardown timings for persistent cluster deployments are **not being captured** in the governance registry CSV (`docs/build-timings.csv`).

The last recorded entry is from `2026-01-01`. The persistent cluster deployment on `2026-01-24` using Bootstrap v4 was not recorded.

## Root Cause Analysis

### Current State

The `scripts/record-build-timing.sh` script captures build timings to `docs/build-timings.csv` with the following schema:

```csv
start_time_utc,end_time_utc,phase,env,build_id,duration_seconds,exit_code,flags,log_path
```

### Where Timing IS Captured

| Makefile Target | Calls `record-build-timing.sh` | Build Type |
|-----------------|-------------------------------|------------|
| `_phase1-infra` | ✅ Yes (line 278) | Ephemeral |
| `_phase2-bootstrap` | ✅ Yes (line 297) | Ephemeral |

### Where Timing IS NOT Captured

| Makefile Target | Calls `record-build-timing.sh` | Build Type |
|-----------------|-------------------------------|------------|
| `apply-persistent` | ❌ No | Persistent |
| `bootstrap-persistent-v4` | ❌ No | Persistent |
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

Add `record-build-timing.sh` calls to persistent cluster targets in the Makefile:

### Option A: Add to Makefile Targets (Recommended)

```makefile
# bootstrap-persistent-v4 target (line 995)
bootstrap-persistent-v4:
	@echo "Bootstrapping persistent cluster..."
	@START_TIME=$$(date -u +%Y-%m-%dT%H:%M:%SZ); \
	# ... existing bootstrap logic ...
	@bash scripts/record-build-timing.sh $(ENV) persistent bootstrap

# teardown-persistent target (line 1042)
teardown-persistent:
	@echo "Tearing down persistent cluster..."
	@START_TIME=$$(date -u +%Y-%m-%dT%H:%M:%SZ); \
	# ... existing teardown logic ...
	@bash scripts/record-build-timing.sh $(ENV) persistent teardown
```

### Option B: Instrument Bootstrap v4 Script

Add timing capture directly in `bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v4.sh`:

```bash
# At script start
START_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# At script end
"${REPO_ROOT}/scripts/record-build-timing.sh" "${ENV}" "${BUILD_ID}" "bootstrap-v4"
```

## Files to Modify

| File | Change |
|------|--------|
| `Makefile` | Add `record-build-timing.sh` calls to persistent targets |
| `bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v4.sh` | (Optional) Add timing capture |

## Acceptance Criteria

1. [ ] Persistent cluster builds are recorded in `docs/build-timings.csv`
2. [ ] Persistent cluster teardowns are recorded in `docs/build-timings.csv`
3. [ ] Build ID is correctly captured (e.g., "persistent" or actual build ID)
4. [ ] Duration is accurately calculated
5. [ ] Exit code is captured for success/failure tracking

## Related Documentation

- ADR-0156: Platform CI Build Timing Capture
- CL-0128: CI Build Timing Capture
- `scripts/record-build-timing.sh` - The timing capture script
- `docs/build-timings.csv` - The timing data store

## Verification Commands

After implementation:

```bash
# Deploy persistent cluster
make deploy-persistent ENV=dev REGION=eu-west-2 BOOTSTRAP_VERSION=v4

# Check if timing was recorded
tail -5 docs/build-timings.csv

# Expected output should include recent entry with phase=bootstrap-v4 or similar
```

## Priority

**Medium** - Not blocking production, but creates observability gap for platform reliability metrics.

## Notes

- The governance registry sync workflow (`governance-registry-writer.yml`) should already handle pushing CSV updates to the governance-registry branch
- Consider whether to backfill historical data or start fresh from implementation date
