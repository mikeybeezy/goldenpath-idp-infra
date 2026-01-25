---
id: CL-0184-fix-duplicate-script-ids
title: 'CL-0184: Fix duplicate SCRIPT IDs in certification matrix'
type: changelog
status: active
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
schema_version: 1
relates_to:
  - SCRIPT-0054
  - SCRIPT-0055
  - SCRIPT-0056
  - SCRIPT-0057
  - SCRIPT_CERTIFICATION_MATRIX
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.5
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# CL-0184: Fix duplicate SCRIPT IDs in certification matrix

## Summary

Fixed 4 duplicate SCRIPT IDs in the certification matrix by assigning unique IDs to scripts that were sharing IDs with other scripts.

## Changes

| Script | Old ID | New ID | Conflict With |
|--------|--------|--------|---------------|
| `inject_script_metadata.py` | SCRIPT-0002 | SCRIPT-0054 | aws_inventory.py |
| `sync_backstage_entities.py` | SCRIPT-0035 | SCRIPT-0055 | rds_provision.py |
| `sync_ecr_catalog.py` | SCRIPT-0036 | SCRIPT-0056 | archive_sessions.py |
| `test_hotfix.py` | SCRIPT-0037 | SCRIPT-0057 | s3_request_parser.py |

## Rationale

Duplicate SCRIPT IDs compromise:
- Script traceability and auditability
- Certification matrix accuracy
- Automated validation of script governance

Each script must have a unique identifier for proper governance tracking.

## Files Changed

- `scripts/inject_script_metadata.py` - Changed ID from SCRIPT-0002 to SCRIPT-0054
- `scripts/sync_backstage_entities.py` - Changed ID from SCRIPT-0035 to SCRIPT-0055
- `scripts/sync_ecr_catalog.py` - Changed ID from SCRIPT-0036 to SCRIPT-0056
- `scripts/test_hotfix.py` - Changed ID from SCRIPT-0037 to SCRIPT-0057

## Related

- Session: session-2026-01-25-governance-metrics-upgrades
