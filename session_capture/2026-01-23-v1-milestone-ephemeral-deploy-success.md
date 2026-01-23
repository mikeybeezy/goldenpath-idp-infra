---
id: 2026-01-23-v1-milestone-ephemeral-deploy-success
title: V1 Milestone - Ephemeral Deploy, DNS Architecture, and Governance Registry Fix
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0177-ci-iam-comprehensive-permissions
  - ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract
  - ADR-0179-dynamic-hostname-generation-ephemeral-clusters
  - RDS_USER_DB_PROVISIONING
  - 2026-01-23-ci-iam-permissions-fix
---
# Session Capture: V1 Milestone - Ephemeral Deploy Success

## Session metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-23
**Timestamp:** 2026-01-23T07:00:00Z
**Branch:** development (goldenpath-idp-infra)

## Scope

- Validate ephemeral cluster deployment as V1 milestone success
- Clarify RDS architecture and dependency chain
- Document standalone RDS deployment workflow
- Merge conflict resolution for PR #275

## Work Summary

### PR #275 Completed

- Resolved merge conflict in `session_summary/agent_session_summary.md`
- Added changelog entry CL-0166 for CI IAM permissions fix
- All 22 CI checks passed
- PR ready for human merge

### V1 Milestone Assessment

Confirmed ephemeral cluster deployment as **success** because:

| Component | Status | Notes |
|-----------|--------|-------|
| CI Pipeline | Working | Commit → Deploy functional |
| VPC/Subnets | Working | Persistent VPC exists |
| EKS cluster | Working | Control plane + nodes up |
| IRSA roles | Working | ESO, ExternalDNS, Autoscaler, ALB |
| ArgoCD | Working | App-of-apps deployed |
| Secrets | Working | Adopt-or-create pattern |
| Keycloak | Pending | Needs standalone RDS |
| Backstage | Pending | Needs standalone RDS |

### RDS Architecture Clarified

**Key insight:** Keycloak/Backstage not working is **expected** - they need standalone RDS deployed first.

**Dependency chain:**
```
1. Persistent VPC (exists) ✓
2. Standalone RDS (envs/dev-rds/) - NEEDS DEPLOYMENT
3. Ephemeral clusters connect to existing RDS
```

**Two RDS workflows explained:**

| Workflow | Purpose | When to use |
|----------|---------|-------------|
| `rds-database-apply.yml` | Deploy RDS instance + pre-configured DBs | First-time setup |
| `create-rds-database.yml` | Add new database to existing RDS | Self-service for new apps |

### Secrets Flow Validated

```
RDS creates: goldenpath/dev/backstage/postgres
  └── { username, password, host, port, dbname }
          ↓
ExternalSecret pulls from Secrets Manager
          ↓
Backstage pod uses credentials
```

## Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Count as V1 success | Yes | Non-DB apps working, DB apps just need RDS |
| RDS deployment approach | Standalone first | ADR-0158 pattern - separate lifecycle |
| Documentation needed | No | Existing docs in RDS_USER_DB_PROVISIONING.md sufficient |

## Artifacts Touched

### Modified

- `session_summary/agent_session_summary.md` - Merged conflict, added sessions
- `docs/changelog/entries/CL-0166-ci-iam-comprehensive-permissions.md` - Created

### Validated

- `gitops/helm/backstage/values/dev.yaml` - ExternalSecret config correct
- `envs/dev-rds/terraform.tfvars` - Pre-configured with keycloak/backstage users
- `envs/dev-rds/main.tf` - Creates secrets with correct structure

## Current State / Follow-ups

**Immediate next step:**
```bash
gh workflow run rds-database-apply.yml -f environment=dev
```

This will:
1. Create RDS PostgreSQL instance
2. Create keycloak + backstage databases
3. Create secrets in Secrets Manager
4. Enable Keycloak/Backstage to connect

**After RDS deployed:**
- Keycloak and Backstage pods will auto-recover
- Full platform stack operational

**PR #275 status:** Ready for human merge

- URL: [PR #275](https://github.com/mikeybeezy/goldenpath-idp-infra/pull/275)

---

## Session Part 2: DNS Architecture and Governance Registry Fix

**Timestamp:** 2026-01-23T10:00:00Z

### ADR-0178 and ADR-0179 Created

Documented the DNS ownership contract for ephemeral vs persistent clusters:

| ADR      | Purpose                                                           | Status   |
|----------|-------------------------------------------------------------------|----------|
| ADR-0178 | Policy - DNS ownership contract and bootstrap mode differentiation | Proposed |
| ADR-0179 | Implementation - BuildId propagation chain for dynamic hostnames   | Proposed |

**Key architecture decision:**

- Persistent clusters own `*.{env}.goldenpathidp.io`
- Ephemeral clusters own `*.b-{buildId}.{env}.goldenpathidp.io`

**BuildId propagation chain (ADR-0179):**
```
CI workflow input → Terraform variable → Helm values → Ingress annotation → ExternalDNS
```

Roadmap items 094-097 added to track implementation.

### PR #276 Gate Fixes

Fixed CI gate failures on hotfix/rds-workflow-backend-config merge to main:

| Issue                                    | Fix                                             |
|------------------------------------------|-------------------------------------------------|
| markdownlint MD034 (bare URL)            | Wrapped URL in markdown link                    |
| emoji-enforcer (non-compliant checkmark) | Replaced checkmark with "DONE" text             |
| require-session-logs                     | Added session entry to agent_session_summary.md |

All 15 checks passed after fixes.

### Governance Registry Bug Investigation and Fix

**Problem:** User reported today's teardowns not appearing in governance-registry logs.

**Investigation findings:**

| Check | Result |
|-------|--------|
| GitHub Actions teardown runs | 4 runs today, 2 successful |
| Teardown logging step | Executed successfully, committed and pushed |
| governance-registry CSV | Only has data up to 2026-01-01 |

**Root cause identified:**

The `governance-registry-writer.yml` workflow was overwriting teardown timing records:

1. Teardown workflow appends row to `environments/development/latest/build_timings.csv`
2. Push to main/development triggers governance-registry-writer
3. Writer copies stale `docs/build-timings.csv` from source branch
4. Fresh teardown data overwritten with stale December 2025 data

**Fix applied (commit d0fcfc11):**

```yaml
# New step added before "Write latest + history"
- name: Preserve existing build_timings.csv
  run: |
    if [ -f "$LATEST_DIR/build_timings.csv" ]; then
      cp "$LATEST_DIR/build_timings.csv" /tmp/preserved_build_timings.csv
    fi

# After copying artifacts, restore preserved file
if [ -f /tmp/preserved_build_timings.csv ]; then
  cp /tmp/preserved_build_timings.csv "$LATEST_DIR/build_timings.csv"
  cp /tmp/preserved_build_timings.csv "$HIST_DIR/build_timings.csv"
fi
```

Also removed the stale copy from source branch that was causing the overwrite.

### Kyverno vs Datree Assessment

Evaluated policy enforcement options:

| Tool | Current State | Recommendation |
|------|---------------|----------------|
| Datree | Deployed as admission webhook but unconfigured (empty values) | Keep for now |
| Kyverno | Not deployed | V1.1/V2 candidate |

**Decision:** Defer Kyverno adoption to V1.1. Admission webhooks can brick clusters if misconfigured - not worth the risk for V1 stability.

## Artifacts Modified (Part 2)

| File | Change |
|------|--------|
| `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md` | Created |
| `docs/adrs/ADR-0179-dynamic-hostname-generation-ephemeral-clusters.md` | Created |
| `docs/adrs/01_adr_index.md` | Added ADR-0178, ADR-0179 |
| `docs/production-readiness-gates/ROADMAP.md` | Added items 094-097 |
| `.github/workflows/governance-registry-writer.yml` | Fixed CSV preservation bug |
| `session_summary/agent_session_summary.md` | Added session entry |

## Current State

| Item | Status |
|------|--------|
| PR #275 | Ready for human merge |
| PR #276 | Ready for human merge |
| Governance registry fix | Pushed to development |
| Next teardown | Will properly log to CSV |

Signed: Claude Opus 4.5 (2026-01-23T10:30:00Z)
