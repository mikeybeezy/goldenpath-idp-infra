---
id: ADR-0156-platform-ci-build-timing-capture
title: 'ADR-0156: CI Build Timing Capture at Source'
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0077-platform-ci-build-teardown-log-automation
  - ADR-0148-seamless-build-deployment-with-immutability
  - ADR-0156-platform-ci-build-timing-capture
  - CL-0128
supersedes: []
superseded_by: []
tags:
  - ci
  - governance
  - observability
  - build-timing
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: medium
  potential_savings_hours: 2.0
supported_until: '2028-01-15'
---

## ADR-0156: CI Build Timing Capture at Source

**Status**: Accepted
**Date**: 2026-01-15
**Relates to**: [ADR-0077](./ADR-0077-platform-ci-build-teardown-log-automation.md), [ADR-0148](./ADR-0148-seamless-build-deployment-with-immutability.md)

## Context

Build timing data for ephemeral cluster deployments was not being captured in the governance-registry `build_timings.csv` when deployments ran through CI workflows.

**The Problem**: The existing `scripts/record-build-timing.sh` script was designed to be called from Makefile targets. However, CI workflows execute `terraform apply` directly without using the Makefile, which meant:

1. CI-triggered builds (e.g., `15-01-26-01` through `15-01-26-08`) were not recorded
2. Only local/manual builds that used `make deploy` were captured
3. The governance-registry CSV showed gaps for all automated deployments

**Why This Matters**:

- Build timing data is essential for platform reliability metrics
- Cost analysis requires accurate deployment duration tracking
- Trend analysis for infrastructure provisioning becomes unreliable

## Decision

We will capture build timing data directly at the source within GitHub Actions workflows, rather than relying on the Makefile-based script.

### Implementation

#### Apply Workflow (`infra-terraform-apply-dev.yml`)

1. **Capture start/end timestamps** around terraform apply:

```yaml
- name: Terraform apply (dev)
  run: |
    echo "TF_APPLY_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${GITHUB_ENV}"
    terraform -chdir=envs/dev apply ... 2>&1 | tee tf_apply.log
    echo "TF_APPLY_END=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${GITHUB_ENV}"
```

1. **Extract resource counts** from terraform output:

```bash
if grep -q "Apply complete!" tf_apply.log; then
  ADDED=$(grep "Apply complete!" tf_apply.log | sed -E 's/.*Resources: ([0-9]+) added.*/\1/')
  CHANGED=$(grep "Apply complete!" tf_apply.log | sed -E 's/.*, ([0-9]+) changed.*/\1/')
  DESTROYED=$(grep "Apply complete!" tf_apply.log | sed -E 's/.*, ([0-9]+) destroyed.*/\1/')
fi
```

1. **Record to governance-registry** branch:

```yaml
- name: Record build timing to governance-registry
  if: always()
  run: |
    git checkout governance-registry
    echo "${START},${END},terraform-apply,dev,${BUILD_ID},${DURATION},..." >> "$CSV_FILE"
    git commit && git push
```

#### Teardown Workflow (`ci-teardown.yml`)

Similar pattern for teardown timing:

- Capture duration from teardown job outputs
- Record phase as `teardown`
- Include workflow run URL for traceability

### CSV Schema

```csv
start_time_utc,end_time_utc,phase,env,build_id,duration_seconds,exit_code,resources_added,resources_changed,resources_destroyed,workflow_run_url
```

The workflow_run_url field provides direct links to GitHub Actions runs for debugging.

## Scope

**Applies to**:

- `infra-terraform-apply-dev.yml` (and staging/prod equivalents)
- `ci-teardown.yml`

**Does not apply to**:

- Local Makefile-based deployments (still use `record-build-timing.sh`)
- Other governance-registry data (scripts_index, adr_index, aws-inventory)

## Consequences

### Positive

- **Reliable capture**: All CI builds are recorded regardless of execution path
- **Accurate timing**: Timestamps captured at exact terraform start/end
- **Rich metadata**: Resource counts, exit codes, and workflow URLs included
- **Append-only**: New data is appended, preserving historical records

### Tradeoffs / Risks

- **Dual paths**: Local builds use script, CI uses inline capture
- **Branch switching**: CI must checkout governance-registry, then return
- **Push conflicts**: Concurrent builds could conflict (mitigated by retry)

### Operational Impact

- **No operator action required**: Change is transparent to users
- **Data continuity**: Historical data preserved, new data appended
- **Monitoring**: Build timing trends now include CI-triggered builds

## Alternatives Considered

### 1. Call `record-build-timing.sh` from CI

Require CI workflows to call the existing script after terraform apply.

**Rejected**: The script relies on local log files in `logs/build-timings/` which CI doesn't generate in the same way. Would require significant script modification.

### 2. Post-deploy webhook

Send timing data to an external service that writes to the registry.

**Rejected**: Adds external dependency and complexity. Direct git operations are simpler and more reliable.

### 3. Parse CI logs retrospectively

Run a scheduled job to extract timing from GitHub Actions logs.

**Rejected**: Complex, prone to breaking on log format changes, and not real-time.

## Follow-ups

1. Extend to staging and prod apply workflows
2. Consider adding bootstrap phase timing capture
3. Evaluate consolidating with Makefile script for unified approach

## Notes

- The `record-build-timing.sh` script remains for local development use
- Other governance-registry files (aws-inventory.md, scripts_index.csv) have separate data sources
- This approach follows the principle of capturing data at the source for accuracy
