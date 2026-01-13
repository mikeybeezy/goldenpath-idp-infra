# ✅ RESOLVED: Build Timings CSV Schema Missing Inventory Columns

> **STATUS**: Fixed on 2026-01-13
> **Commit**: `f629112f` on governance-registry branch
> **Resolution**: Added inventory columns and backfilled 38 historical records

## Issue Summary (RESOLVED)

The `build_timings.csv` file in the governance-registry branch **was missing** critical inventory tracking columns that exist in the local `docs/build-timings.csv`:

### Old Schema (BEFORE FIX - 9 columns)
```csv
start_time_utc,end_time_utc,phase,env,build_id,duration_seconds,exit_code,flags,log_path
```

### Fixed Schema (AFTER FIX - 12 columns)
```csv
start_time_utc,end_time_utc,phase,env,build_id,duration_seconds,exit_code,flags,resources_added,resources_changed,resources_destroyed,log_path
```

### Missing Columns
- `resources_added` - Count of resources created during terraform apply
- `resources_changed` - Count of resources modified during terraform apply
- `resources_destroyed` - Count of resources destroyed during terraform apply

## Impact

**Data Loss**: Without these columns, we lose the ability to:
1. Track infrastructure inventory changes over time
2. Understand what was built in each deployment
3. Calculate infrastructure growth rates
4. Correlate resource counts with build duration
5. Identify deployments that added/removed significant resources

## Root Cause

The governance-registry CSV was created or migrated without including the inventory columns that were present in the original `docs/build-timings.csv`.

## ✅ Resolution (Completed 2026-01-13)

### Actions Taken

**1. Updated CSV Header**
- Added 3 inventory columns to governance-registry CSV
- Header now has 12 columns (was 9)
- Commit: `f629112f` on governance-registry branch

**2. Backfilled Historical Records**
- Processed 38 existing records
- Added `0,0,0` for missing inventory data
- Fixed 1 record missing phase column (set to "unknown")
- All 39 lines validated to have 12 columns

**3. Verified Fix**
```bash
# Verified header
$ git show origin/governance-registry:environments/development/latest/build_timings.csv | head -1 | awk -F',' '{print NF}'
12  # ✅ Correct

# Verified all rows
$ git show origin/governance-registry:environments/development/latest/build_timings.csv | awk -F',' '{print NF}' | sort | uniq -c
  39 12  # ✅ All rows have 12 columns
```

**4. Documentation Updated**
- Updated how-it-works guide with CSV schema section
- Removed critical warnings (issue resolved)
- This file updated to reflect resolution status

### Remaining Actions (For CI/CD Workflows)

## Required Actions (Future Builds)

### 1. Update governance-registry CSV Header

The CSV header in `governance-registry:environments/development/latest/build_timings.csv` must be updated to:

```csv
start_time_utc,end_time_utc,phase,env,build_id,duration_seconds,exit_code,flags,resources_added,resources_changed,resources_destroyed,log_path
```

### 2. Backfill Existing Records

Existing records in governance-registry should be backfilled with empty values for inventory columns:

```bash
# For each existing record, insert empty inventory columns before log_path
# Old: start,end,phase,env,build_id,duration,exit_code,flags,log_path
# New: start,end,phase,env,build_id,duration,exit_code,flags,,,log_path
#                                                              ^^^ empty inventory columns
```

### 3. Update CI/CD Workflows

All workflows that append to `build_timings.csv` must include inventory data:

```yaml
- name: Extract Terraform Inventory
  run: |
    RESOURCES_ADDED=$(grep -oP 'Plan: \K\d+(?= to add)' terraform_output.txt || echo "0")
    RESOURCES_CHANGED=$(grep -oP ', \K\d+(?= to change)' terraform_output.txt || echo "0")
    RESOURCES_DESTROYED=$(grep -oP ', \K\d+(?= to destroy)' terraform_output.txt || echo "0")

    echo "RESOURCES_ADDED=$RESOURCES_ADDED" >> $GITHUB_ENV
    echo "RESOURCES_CHANGED=$RESOURCES_CHANGED" >> $GITHUB_ENV
    echo "RESOURCES_DESTROYED=$RESOURCES_DESTROYED" >> $GITHUB_ENV

- name: Record Build Timing
  run: |
    echo "$START_TIME,$END_TIME,$PHASE,dev,$BUILD_ID,$DURATION,$EXIT_CODE,\"$FLAGS\",$RESOURCES_ADDED,$RESOURCES_CHANGED,$RESOURCES_DESTROYED,$LOG_PATH" >> build_timings.csv
```

### 4. Update Documentation

Update the following files to reference the correct schema:

- `docs/how-it-works/BUILD_ID_IMMUTABILITY_ENFORCEMENT.md`
- `docs/adrs/ADR-0153-build-id-immutability-enforcement.md`
- `docs/changelog/entries/CL-0125-build-id-immutability-enforcement.md`

## Verification

After fix, verify the schema matches:

```bash
# Check governance-registry header
git show origin/governance-registry:environments/development/latest/build_timings.csv | head -1

# Should output (12 columns):
# start_time_utc,end_time_utc,phase,env,build_id,duration_seconds,exit_code,flags,resources_added,resources_changed,resources_destroyed,log_path

# Verify column count
git show origin/governance-registry:environments/development/latest/build_timings.csv | head -1 | awk -F',' '{print NF}'
# Should output: 12
```

## Example Record with Inventory

```csv
2026-01-13T10:30:00Z,2026-01-13T10:45:00Z,terraform-apply,dev,13-01-26-01,900,0,"ENV_NAME=dev",47,12,0,logs/build-timings/dev-13-01-26-01-20260113T103000Z.log
```

This record shows:
- **47 resources added** (new infrastructure)
- **12 resources changed** (updated configuration)
- **0 resources destroyed** (no deletions)

## Priority

**CRITICAL** - This should be fixed before the next build:
1. Without inventory columns, the validation still works (grep only checks env/build_id)
2. But we permanently lose historical inventory data for any builds that run before fix
3. Inventory data is essential for capacity planning and cost analysis

## Timeline

- **Immediate**: Document the issue (this file)
- **Next PR**: Fix governance-registry CSV header and backfill
- **Before next build**: Update CI/CD workflows to populate inventory columns
- **After fix**: Update all documentation to reference correct schema

## Related Files

- Local reference: [docs/build-timings.csv](./build-timings.csv) (correct schema)
- Registry location: `origin/governance-registry:environments/development/latest/build_timings.csv` (needs fix)
- Validation code: [envs/dev/main.tf](../envs/dev/main.tf) (lines 25-50)
- Documentation:
  - [docs/how-it-works/BUILD_ID_IMMUTABILITY_ENFORCEMENT.md](./how-it-works/BUILD_ID_IMMUTABILITY_ENFORCEMENT.md)
  - [docs/adrs/ADR-0153-build-id-immutability-enforcement.md](./adrs/ADR-0153-build-id-immutability-enforcement.md)
  - [docs/changelog/entries/CL-0125-build-id-immutability-enforcement.md](./changelog/entries/CL-0125-build-id-immutability-enforcement.md)

## Contact

- **Discovered**: 2026-01-13
- **Reporter**: Platform Team
- **Severity**: Critical (data loss)
- **Status**: Documented, awaiting fix
