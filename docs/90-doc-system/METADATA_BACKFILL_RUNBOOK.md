---
id: METADATA_BACKFILL_RUNBOOK
title: Metadata Backfill Runbook
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0082
  - ADR-0083
  - ADR-XXXX
  - CL-XXXX
  - METADATA_STRATEGY
  - METADATA_VALIDATION_GUIDE
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
status: active
version: '1.0'
dependencies: []
supported_until: 2027-01-03
breaking_change: false
---

## Metadata Backfill Runbook

Purpose: Backfill metadata for docs and Terraform with deterministic steps and
audit trails, while keeping changes small and reversible.

Scope:

- Markdown under `docs/`.
- Terraform resources in `*.tf`.

Non-goals:

- Enforce metadata for source code headers. That is a future phase.

References:

- `docs/90-doc-system/METADATA_STRATEGY.md`
- `docs/90-doc-system/METADATA_VALIDATION_GUIDE.md`
- `scripts/validate_metadata.py`

## Phase 0: Prep

1. Sync with base and create a branch.
2. Confirm the current validator scope:
   - `validate_metadata.py` only checks `docs/adrs/`, `docs/changelog/entries/`,
     and `docs/10-governance/`.
3. Decide the batch size (default: 10 files per commit).
4. Create an audit note (optional but recommended):
   - `docs/90-doc-system/metadata-backfill/audit-YYYYMMDD.md`

## Phase 1: Documentation Backfill (Markdown)

### Step 1: Discovery (Audit)

```bash
python3 scripts/validate_metadata.py docs | tee audit_report.txt
grep '\\[MISSING\\]' audit_report.txt > missing_frontmatter.txt
```

If the validator output format changes, manually review the report and create
`missing_frontmatter.txt` by hand.

### Step 2: Deterministic Frontmatter Rules

Use the following rules for each file:

ID rules:

- `docs/adrs/ADR-XXXX-*.md` -> `id: ADR-XXXX` (must match filename).
- `docs/changelog/entries/CL-XXXX-*.md` -> `id: CL-XXXX`.
- Otherwise -> `id: DOC-###` (use the next available number; scan for `id: DOC-`).

Type rules:

- `docs/adrs/` -> `adr`
- `docs/changelog/entries/` -> `changelog`
- `docs/70-operations/runbooks/` -> `runbook`
- `docs/10-governance/policies/` -> `policy`
- Otherwise -> `topic`

Owner rules:

- If the file declares a team or author, use it.
- Otherwise, default to `platform-team`.

Status rules:

- ADRs: map `Status: Accepted` -> `active`, `Deprecated` -> `deprecated`.
- Otherwise, default to `active`.

### Step 3: Apply Frontmatter

Prepend a YAML block to each file using the schema in
`docs/90-doc-system/METADATA_STRATEGY.md`.

### Step 4: Verify Per File

```bash
python3 scripts/validate_metadata.py <file_path>
```

If a file fails validation, revert the file and log it in the audit note.

### Step 5: Batch Commit

Process 10 files, then commit:

```bash
git commit -m "docs(metadata): backfill batch <N>"
```

## Phase 2: Infrastructure Backfill (Terraform)

### Step 1: Locate Missing Tags

Identify resources missing `tags` or `tags_all`:

```bash
rg -n 'resource "aws_' -g '*.tf'
```

### Step 2: Ensure Tag Inputs

If a module has no tag input, add:

```hcl
variable "tags" {
  description = "Metadata: Owner, Service, CostCenter"
  type        = map(string)
}
```

### Step 3: Inject Tags Safely

Use merge to preserve existing tags:

```hcl
tags = merge(var.tags, {
  Name = "specific-resource-name"
})
```

Do not add tags to resources that do not support them.

## Phase 3: Source Code Headers (Future)

Only implement when validation exists. For now, track scripts that should
receive structured headers in the audit note.

## Quality Gate

Required:

- `python3 scripts/validate_metadata.py docs` returns exit code 0.
- `terraform validate` passes for the scoped directory.
- `make plan ENV=dev` shows no destructive changes (tag-only updates).

## Rollback

Revert the batch commit:

```bash
git revert <commit_sha>
```
