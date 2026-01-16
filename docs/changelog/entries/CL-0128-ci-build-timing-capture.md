---
id: CL-0128
title: CI Build Timing Capture at Source
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - infra-terraform-apply-dev.yml
  - ci-teardown.yml
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
schema_version: 1
relates_to:
  - ADR-0156-platform-ci-build-timing-capture
  - ADR-0077-platform-ci-build-teardown-log-automation
supersedes: []
superseded_by: []
tags:
  - ci
  - governance
  - observability
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: medium
  potential_savings_hours: 2.0
supported_until: 2028-01-15
date: 2026-01-15
author: platform-team
breaking_change: false
---

## Summary

- Added direct build timing capture to CI workflows
- CI-triggered builds now record to governance-registry `build_timings.csv`
- Fixes gap where CI builds were not being tracked

## Impact

- **Platform team**: Build timing data now includes all CI deployments
- **Governance**: Complete build history for reliability metrics
- **No user action required**: Change is transparent

## Changes

### Added

- **Apply workflow timing**: Captures terraform apply start/end timestamps
- **Resource count extraction**: Parses `Apply complete!` output for +/-/~ counts
- **Teardown timing**: Records teardown duration and outcome
- **Workflow URL tracking**: Links each record to GitHub Actions run

### Changed

- `infra-terraform-apply-dev.yml`: Added timing capture around terraform apply
- `ci-teardown.yml`: Added timing recording in log-generation job

### Fixed

- CI builds (15-01-26-xx series) now appear in governance-registry CSV
- Build timing trend analysis includes automated deployments

## Files Changed

### Workflows
- `.github/workflows/infra-terraform-apply-dev.yml`
  - Added `contents: write` permission
  - Modified terraform apply step to capture timing
  - Added `Record build timing to governance-registry` step
- `.github/workflows/ci-teardown.yml`
  - Added `Record teardown timing to governance-registry` step

### Documentation
- `docs/adrs/ADR-0156-platform-ci-build-timing-capture.md` - New ADR

## Technical Details

### Data Flow

```text
CI Workflow                           Governance Registry
-----------                           -------------------
terraform apply start
    |
    v
TF_APPLY_START=$(date -u)
    |
terraform -chdir=envs/dev apply
    |
    v
TF_APPLY_END=$(date -u)
    |
Parse "Apply complete!" for counts
    |
    v
git checkout governance-registry  --> environments/development/latest/
    |                                     build_timings.csv
echo "..." >> build_timings.csv   -->   [appends new row]
    |
git push origin governance-registry
```

### CSV Schema

| Field | Description |
|-------|-------------|
| start_time_utc | ISO8601 timestamp of terraform start |
| end_time_utc | ISO8601 timestamp of terraform end |
| phase | `terraform-apply` or `teardown` |
| env | Environment name (dev, staging, prod) |
| build_id | Build identifier or "persistent" |
| duration_seconds | Calculated duration |
| exit_code | Terraform exit code (0=success) |
| resources_added | Count from terraform output |
| resources_changed | Count from terraform output |
| resources_destroyed | Count from terraform output |
| workflow_run_url | Link to GitHub Actions run |

## Known Limitations

- Local Makefile builds still use `record-build-timing.sh` (separate path)
- Concurrent CI builds could have push conflicts (mitigated by retry logic)

## Rollback / Recovery

```bash
git revert <commit-sha>
```

Timing capture is additive. Removing it simply stops new records; existing data is preserved.

## Validation

- Build 15-01-26-09 triggered with new timing capture
- Verified CSV append logic preserves existing records
- Tested branch checkout/push cycle
