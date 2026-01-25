<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0140
title: Automated RDS User and Database Provisioning
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - scripts/rds_provision.py
  - Makefile
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: medium
  coupling_risk: low
schema_version: 1
relates_to:
  - ADR-0165
  - CL-0140
  - PRD-0001-rds-user-db-provisioning
  - RB-0030-rds-break-glass-deletion
  - RB-0032
  - SCRIPT-0035
  - agent_session_summary
supersedes: []
superseded_by: []
tags:
  - rds
  - provisioning
  - database
  - automation
inheritance: {}
supported_until: 2028-01-16
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: high
  potential_savings_hours: 40.0
date: 2026-01-16
author: platform-team
breaking_change: false
---

## Summary

- Automated RDS user and database provisioning driven by `application_databases` in tfvars
- Idempotent role/database creation with access-level grants (owner/editor/reader)
- Fail-fast behavior on missing secrets or connection errors
- Persistent audit trail to `governance/<env>/rds_provision_audit.csv`

## Impact

- **Platform team**: Eliminates manual `psql` provisioning; reduces drift between secrets and DB state
- **Application teams**: New app database definitions provision automatically without tickets
- **Governance**: Full audit trail with build_id, run_id, and per-operation status

## Changes

### Added

- `scripts/rds_provision.py` (SCRIPT-0035): Core provisioning script
  - Parses `application_databases` from terraform.tfvars
  - Fetches credentials from AWS Secrets Manager
  - Creates roles/databases idempotently via psycopg2
  - Applies grants per access level (owner/editor/reader)
  - Emits CSV audit records

- `tests/scripts/test_script_0035.py`: Unit tests for provisioning logic

- `docs/70-operations/runbooks/RB-0032-rds-user-provision.md`: Operations runbook

- Makefile targets:
  - `make rds-provision ENV=<env>` - Execute provisioning
  - `make rds-provision-dry-run ENV=<env>` - Preview without changes

### Changed

- Updated ADR-0165 status from "proposed" to "accepted"

### Security

- Approval gate: `ALLOW_DB_PROVISION=true` required for non-dev environments
- Passwords masked in logs
- SSL required for all RDS connections

## Rollback / Recovery

```bash
# Roles/databases created are persistent; no automatic rollback
# Manual removal if needed (see RB-0030 for deletion):
psql -h <endpoint> -U platform_admin -c "DROP DATABASE <db>"
psql -h <endpoint> -U platform_admin -c "DROP ROLE <role>"
```

## Validation

```bash
# Dry run (no changes)
make rds-provision-dry-run ENV=dev

# Verify idempotence (run twice, second shows no_change)
make rds-provision ENV=dev
make rds-provision ENV=dev

# Check audit trail
cat governance/dev/rds_provision_audit.csv
```

## Related Documentation

- [PRD-0001: RDS User and Database Provisioning](../../20-contracts/prds/PRD-0001-rds-user-db-provisioning.md)
- [ADR-0165: Automated RDS Provisioning](../../adrs/ADR-0165-rds-user-db-provisioning-automation.md)
- [RB-0032: RDS User Provision Runbook](../../70-operations/runbooks/RB-0032-rds-user-provision.md)
