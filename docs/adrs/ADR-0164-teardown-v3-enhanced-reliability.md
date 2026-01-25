<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: ADR-0164-teardown-v3-enhanced-reliability
title: 'ADR-0164: Teardown V3 with Enhanced Reliability and RDS Support'
type: adr
status: active
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: high
  potential_savings_hours: 4.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: manual
  observability_tier: gold
schema_version: 1
relates_to:
  - 01_adr_index
  - 15_TEARDOWN_AND_CLEANUP
  - ADR-0038-platform-teardown-orphan-cleanup-gate
  - ADR-0043-platform-teardown-lb-eni-wait
  - ADR-0045-platform-teardown-lb-delete-default
  - ADR-0047-platform-teardown-destroy-timeout-retry
  - ADR-0048-platform-teardown-version-selector
  - ADR-0164-teardown-v3-enhanced-reliability
  - CL-0139-teardown-v3-enhanced-reliability
supersedes:
  - ADR-0048-platform-teardown-version-selector
superseded_by: []
tags:
  - teardown
  - eks
  - rds
  - reliability
inheritance: {}
supported_until: 2028-01-16
version: '1.0'
breaking_change: false
---

# ADR-0164: Teardown V3 with Enhanced Reliability and RDS Support

Filename: `ADR-0164-teardown-v3-enhanced-reliability.md`

- **Status:** Active
- **Date:** 2026-01-16
- **Owners:** `platform-team`
- **Domain:** Platform
- **Decision type:** Operations
- **Related:**
  - `bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v3.sh`
  - `bootstrap/60_tear_down_clean_up/cleanup-orphans.sh`
  - `.github/workflows/ci-teardown.yml`
  - `docs/70-operations/15_TEARDOWN_AND_CLEANUP.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

### Problem Statement

Teardown V2 experienced failures in CI when the Kubernetes API became unreachable:

```
ResourceInUseException: Cluster has nodegroups attached
```

**Root Cause Analysis:**

1. V2 script at line 671 checked both `cluster_exists` AND `kube_access` before deleting nodegroups
2. When k8s API was down, `kube_access="false"` caused nodegroup deletion to be skipped
3. Orphan cleanup found nodegroups but didn't wait for deletion before attempting cluster deletion
4. Terraform destroy failed because nodegroups were still attached

**Additional Gaps:**

- RDS instances introduced in the platform were not included in teardown
- CI logs showed "UNKNOWN STEP" labels, making troubleshooting difficult
- LoadBalancer ENI cleanup ordering was not deterministic

### Requirements

1. Nodegroup deletion must work even when Kubernetes API is unavailable
2. RDS instances must be cleaned up during teardown
3. Every operation must have explicit step logging for CI visibility
4. LoadBalancer cleanup must follow proper ordering: Services -> LBs -> Target Groups -> ENIs
5. Break-glass operations must be clearly labeled

---

## Decision

We will introduce **Teardown V3** as the new default, implementing:

### 1. Decoupled Nodegroup Deletion

Nodegroup deletion via AWS CLI is now independent of Kubernetes API access:

```bash
# V2 (broken when k8s API down):
if [[ "${cluster_exists}" == "false" || "${kube_access}" == "false" ]]; then
  echo "Skipping nodegroup deletion..."

# V3 (works regardless of k8s API):
if [[ "${cluster_exists}" == "false" ]]; then
  log_info "Cluster does not exist; skipping nodegroup deletion."
else
  delete_nodegroups_via_aws
  wait_for_nodegroup_deletion
fi
```

### 2. 8-Stage Teardown Sequence

| Stage | Purpose | Dependencies |
|-------|---------|--------------|
| 1 | Cluster Validation | None |
| 2 | Pre-Destroy Cleanup (K8s) | K8s API optional |
| 3 | Drain Nodegroups | K8s API required |
| 4 | Delete Nodegroups (AWS) | Cluster exists only |
| 5 | Delete RDS Instances | BuildId tag |
| 6 | Terraform Destroy | State access |
| 7 | Orphan Cleanup | BuildId tag |
| 8 | Teardown Complete | None |

### 3. Explicit Step Logging

All operations use structured prefixes:

- `[STEP: NAME]` - Major operation starting
- `[INFO]` - Informational messages
- `[WARN]` - Warning conditions
- `[ERROR]` - Error conditions
- `[BREAK-GLASS]` - Emergency cleanup operations
- `[HEARTBEAT]` - Long-running operation progress
- `[WAIT]` - Waiting for condition with timeout

### 4. RDS Cleanup Support

New environment variables:
- `DELETE_RDS_INSTANCES=true|false` (default true)
- `RDS_SKIP_FINAL_SNAPSHOT=true|false` (default true for ephemeral)
- `RDS_DELETE_AUTOMATED_BACKUPS=true|false` (default true)

### 5. Enhanced Orphan Cleanup (v2.0.0)

- Added nodegroup wait loop with configurable timeout
- Added RDS instance, subnet group, and parameter group cleanup
- Added target group cleanup
- All operations have structured logging

---

## Scope

### Applies to

- CI teardown workflow (`ci-teardown.yml`)
- Manual Makefile teardown targets
- Orphan cleanup scripts

### Does not apply to

- Bootstrap or infrastructure apply flows
- Local Kind cluster teardown

---

## Consequences

### Positive

- Eliminates `ResourceInUseException` failures from nodegroup timing
- RDS resources are properly cleaned up
- CI logs are fully traceable (no "UNKNOWN STEP")
- Break-glass operations are auditable
- LoadBalancer cleanup follows deterministic ordering

### Tradeoffs / Risks

- Three teardown script versions to maintain (v1, v2, v3)
- V3 takes slightly longer due to explicit waits
- RDS cleanup adds additional time for environments with databases

### Operational Impact

- V3 is now the default in CI and Makefile
- Operators can still select v1 or v2 via `TEARDOWN_VERSION` if needed
- Runbooks should be updated to reference v3 behavior

---

## Alternatives Considered

1. **Patch V2 in place:** Risks breaking existing workflows
2. **Merge all versions into one with feature flags:** Increases complexity
3. **Remove k8s API check entirely:** Would skip useful drain operations

---

## Migration Path

1. V3 is deployed as the new default (this ADR)
2. V2 remains available for rollback if needed
3. After 30 days of stability, V1 and V2 can be deprecated
4. Future changes should be V3 patches or a new V4

---

## Files Changed

| File | Change |
|------|--------|
| `bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v3.sh` | New script |
| `bootstrap/60_tear_down_clean_up/cleanup-orphans.sh` | Updated to v2.0.0 |
| `.github/workflows/ci-teardown.yml` | Default changed to v3 |
| `Makefile` | Default changed to v3, case statement for version selection |

---

## Follow-ups

- [ ] Update teardown runbook with v3 stage descriptions
- [ ] Add v3 to script certification matrix
- [ ] Monitor CI teardown success rate for 2 weeks
- [ ] Deprecate v1/v2 after 30-day stability period

---

## Notes

This ADR **supersedes ADR-0048** which established the v1/v2 versioning pattern.
The pattern is extended to include v3 as the new default.
