---
id: CL-0139-teardown-v3-enhanced-reliability
title: Teardown V3 with Enhanced Reliability and RDS Support
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - teardown
  - eks
  - rds
  - cleanup
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: version-selector
  observability_tier: gold
schema_version: 1
relates_to:
  - 15_TEARDOWN_AND_CLEANUP
  - ADR-0038-platform-teardown-orphan-cleanup-gate
  - ADR-0048-platform-teardown-version-selector
  - ADR-0164-teardown-v3-enhanced-reliability
  - CL-0139-teardown-v3-enhanced-reliability
supersedes:
  - ADR-0048-platform-teardown-version-selector
superseded_by: []
tags:
  - teardown
  - reliability
  - rds
  - nodegroup
  - break-glass
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: high
  potential_savings_hours: 4.0
supported_until: 2028-01-16
version: '1.0'
breaking_change: false
---

## CL-0139: Teardown V3 with Enhanced Reliability and RDS Support

**Type**: Feature / Fix
**Component**: Teardown Infrastructure
**Date**: 2026-01-16

### Summary

Introduces Teardown V3, a comprehensive rewrite of the EKS cluster teardown system that fixes critical reliability issues and adds RDS cleanup support. V3 is now the default for all teardown operations.

### Problem Solved

CI teardown failures were occurring with:
```
ResourceInUseException: Cluster has nodegroups attached
```

**Root Cause**: V2 script skipped nodegroup deletion when Kubernetes API was unreachable, but the orphan cleanup then tried to delete the cluster before nodegroups were removed.

### Changes

#### New Files

| File | Description |
|------|-------------|
| `bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v3.sh` | Enhanced teardown with 8-stage sequence |

#### Modified Files

| File | Change |
|------|--------|
| `bootstrap/60_tear_down_clean_up/cleanup-orphans.sh` | Updated to v2.0.0 with nodegroup wait and RDS support |
| `.github/workflows/ci-teardown.yml` | Default version changed to v3 |
| `Makefile` | Default version changed to v3, case statement for version selection |

### Key Improvements

#### 1. Nodegroup Deletion Independence

Nodegroups are now deleted via AWS CLI regardless of Kubernetes API availability:

```bash
# Only skip if cluster doesn't exist (not if k8s API is down)
if [[ "${cluster_exists}" == "false" ]]; then
  log_info "Cluster does not exist; skipping nodegroup deletion."
else
  delete_nodegroups_via_aws
  wait_for_nodegroup_deletion  # Explicit wait loop
fi
```

#### 2. 8-Stage Teardown Sequence

| Stage | Purpose |
|-------|---------|
| 1 | Cluster Validation |
| 2 | Pre-Destroy Cleanup (K8s resources) |
| 3 | Drain Nodegroups (if k8s accessible) |
| 4 | Delete Nodegroups (AWS CLI) |
| 5 | Delete RDS Instances |
| 6 | Terraform Destroy |
| 7 | Orphan Cleanup |
| 8 | Teardown Complete |

#### 3. Explicit Step Logging

No more "UNKNOWN STEP" in CI logs. Every operation uses:
- `[STEP: NAME]` - Major operation
- `[INFO]` - Informational
- `[WARN]` - Warnings
- `[ERROR]` - Errors
- `[BREAK-GLASS]` - Emergency cleanup
- `[HEARTBEAT]` - Progress updates
- `[WAIT]` - Timeout tracking

#### 4. RDS Cleanup Support

New Stage 5 handles RDS resources:
- RDS instances (with optional final snapshot)
- RDS subnet groups
- RDS parameter groups

Environment variables:
- `DELETE_RDS_INSTANCES=true|false`
- `RDS_SKIP_FINAL_SNAPSHOT=true|false`
- `RDS_DELETE_AUTOMATED_BACKUPS=true|false`

#### 5. LoadBalancer Cleanup Ordering

Proper sequence ensures no dangling resources:
1. Delete LoadBalancer services (k8s)
2. Remove service finalizers (if stuck)
3. Scale down LB controller
4. Delete load balancers (AWS)
5. Delete target groups (AWS)
6. Wait for ENI cleanup

#### 6. Enhanced Orphan Cleanup (v2.0.0)

- Nodegroup wait loop with configurable timeout (default 600s)
- RDS instance, subnet group, and parameter group cleanup
- Target group cleanup
- Structured logging throughout

### Testing

```bash
# Syntax validation
bash -n bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v3.sh

# Dry run (prints commands without executing)
TEARDOWN_VERSION=v3 TEARDOWN_CONFIRM=true make teardown \
  ENV=dev BUILD_ID=test CLUSTER=test-cluster REGION=eu-west-2
```

### Rollback

If issues occur, revert to v2:
```bash
TEARDOWN_VERSION=v2 make teardown ...
```

Or via CI workflow dispatch, select `v2` from the version dropdown.

### Related

- **ADR**: [ADR-0164-teardown-v3-enhanced-reliability](../adrs/ADR-0164-teardown-v3-enhanced-reliability.md)
- **Supersedes**: [ADR-0048-platform-teardown-version-selector](../adrs/ADR-0048-platform-teardown-version-selector.md)
- **Runbook**: [09_CI_TEARDOWN_RECOVERY_V2.md](../runbooks/09_CI_TEARDOWN_RECOVERY_V2.md)

### Version History

| Version | Date | Changes |
|---------|------|---------|
| v3.0.0 | 2026-01-16 | Initial v3 release |
| cleanup-orphans v2.0.0 | 2026-01-16 | Added nodegroup wait, RDS support |
