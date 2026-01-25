---
id: RB-0028
title: Governance Registry Branch Operations
type: runbook
domain: operations
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 1
schema_version: 1
relates_to:
  - ADR-0145
  - CAPABILITY_LEDGER
  - CL-0114
  - DOCS_RUNBOOKS_README
supersedes: []
superseded_by: []
tags: []
inheritance: {}
status: active
supported_until: '2028-01-01'
date: 2026-01-12
---

# RB-0028: Governance Registry Branch Operations

## Purpose
The `governance-registry` branch is a CI-owned "observation context" that stores **derived-only** governance artifacts:
- Platform health reports
- Documentation indices
- Catalog sync outputs
- Audit logs

This prevents "commit tug-of-war" on human development branches while preserving a durable, git-native audit trail.

## Source of Truth Contract
- `development` and `main` are canonical for **intent** (code, configs, contracts, schemas).
- `governance-registry` is canonical for **observation** (reports + indices).
- Registry artifacts MUST be reproducible from a specific `source_sha`.
- Humans do not manually patch registry outputs.

## Directory Layout

```text
governance-registry/
├── UNIFIED_DASHBOARD.md
└── environments/
    ├── development/
    │   ├── latest/
    │   │   ├── PLATFORM_HEALTH.md
    │   │   ├── scripts_index.md
    │   │   ├── workflows_index.md
    │   │   └── catalogs_index.md
    │   └── history/
    │       └── <date>-<sha>/
    │           ├── PLATFORM_HEALTH.md
    │           ├── scripts_index.md
    │           ├── workflows_index.md
    │           └── catalogs_index.md
    └── production/
        ├── latest/
        └── history/
```

## Artifact Header Requirements
Every Markdown artifact written into `governance-registry` MUST include a frontmatter header for chain-of-custody.

**Required fields:**
- `env`
- `generated_at` (UTC)
- `source.branch`
- `source.sha`
- `pipeline.workflow`
- `pipeline.run_id`
- `integrity.derived_only`

**Example:**
```yaml
---
type: governance-report
env: development
generated_at: 2026-01-12T08:14:03Z
source:
  branch: development
  sha: c420fca
pipeline:
  workflow: governance-registry-writer.yml
  run_id: 12345678
integrity:
  derived_only: true
---
```

## Write Boundary (Integrity Control)
Only CI may push to `governance-registry`.

**Branch protection settings:**
- Restrict who can push: ✅ Enabled
- Allow GitHub Actions / CI bot identity: ✅ Enabled
- Force pushes:  Disabled

## Concurrency / Ordering
Registry updates must be **atomic**:
1. Update `latest/`
2. Append to `history/<date>-<sha>/`
3. Update `UNIFIED_DASHBOARD.md`

All in a single commit.

CI must apply concurrency grouping per environment to prevent race conditions:
```yaml
concurrency:
  group: govreg-${{ github.ref_name }}
  cancel-in-progress: false
```

## Troubleshooting

### "Registry did not update"
**Check:**
- Audit workflow ran on merge to `development` or `main`
- CI has `write` permission to `contents`
- Branch protection allows CI identity
- Concurrency group is not blocked by a stuck run

### "Latest updated but history missing"
This indicates a non-atomic commit.

**Fix:**
- Rerun the registry writer job
- Ensure writer always updates `latest` + `history` in the same commit

### "Human committed to registry"
This is a **policy violation**.

**Fix:**
- Revert commit
- Restore branch protection
- Rotate bot token if required

## Operational Notes
- Registry growth is expected. If repo size becomes an issue, apply a retention policy (future).
- Registry artifacts are not "hand-edited documentation"; they are derived outputs.
- All consumers (Backstage, README) should link to `governance-registry/environments/<env>/latest/`.
