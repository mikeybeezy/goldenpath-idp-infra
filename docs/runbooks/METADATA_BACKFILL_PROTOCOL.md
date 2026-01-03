---
id: RUNBOOK-0005
title: Metadata Backfill Protocol (Agentic)
type: runbook
owner: platform-team
status: active
relates_to:
  - METADATA_STRATEGY
  - ADR-0081
---

# 🤖 Protocol: Metadata Backfill Campaign

**Objective:** Systematically update repository artifacts to adhere to the Metadata Schema defined in `METADATA_STRATEGY.md`. This protocol is designed for autonomous agents to execute deterministically.

**Scope:**
*   **Phase 1:** Documentation (`.md`)
*   **Phase 2:** Infrastructure (`.tf`)
*   **Phase 3 (Future):** Source Code (`.py`, `.sh`, `.Dockerfile`) - *Header Standardization Only*

**Safety Rules:**
1.  **Do No Harm:** If a file cannot be parsed or updated safely, SKIP IT and log to `audit_skipped.json`.
2.  **Deterministic IDs:** Use existing IDs or generate new ones via Registry. Never guess.
3.  **Atomic Batches:** Commit every 10 files. PR every Phase.

---

## 🔁 Phase 1: Documentation Backfill (Markdown)

### 1. Discovery (Dry Run)
Use the validator's JSON mode to find non-compliant files without brittle text parsing.

```bash
python3 scripts/validate-metadata.py docs --json > backfill_audit.json
```
*   **Target:** Files with `status: missing`.
*   **Exclusions:** `README.md`, `DOC_INDEX.md`, `templates/`, `node_modules/`, `vendor/`.

### 2. Execution Logic (Per File)
For each target file:

**A. ID Resolution:**
*   **If filename matches ID pattern** (e.g. `ADR-0021-title.md`):
    *   Extract ID: `ADR-0021`.
*   **If filename is generic** (e.g. `troubleshooting.md`):
    *   Check `docs/20-contracts/DOC_REGISTRY.md`.
    *   If found: Use registered ID.
    *   If not found: Generate `DOC-<HASH-8>` (e.g., `DOC-A1B2C3D4`) and append to Registry.

**B. Field Extraction:**
*   **Owner:** Regex search for `Author: (.*)` or `Owner: (.*)`. Default: `platform-team`.
*   **Type:**
    *   `docs/adrs/*` -> `adr`
    *   `docs/changelog/*` -> `changelog`
    *   `docs/policies/*` -> `policy`
    *   `docs/runbooks/*` -> `runbook`
    *   Else -> `topic`
*   **Status:** Default `active` unless `Deprecated` found in text.

**C. Injection:**
Prepend the YAML block. Preserve original content exactly.

```yaml
---
id: <ID>
title: <H1 from content or Filename>
type: <type>
owner: <owner>
status: <status>
---
```

**D. Verification:**
Run `python3 scripts/validate-metadata.py <file_path>`. MUST pass.

### 3. Batching & Audit
*   **Batch Size:** 10 Files.
*   **Commit Message:** `docs(metadata): backfill batch <N> [skip ci]`
*   **Audit Artifact:** Write `backfill_report_phase1.json` listing all updated files and assigned IDs.

---

## 🔁 Phase 2: Infrastructure Backfill (Terraform)

### 1. Discovery
Scan `*.tf` files for `resource "aws_..."` blocks.
*   **Target:** Resources NOT containing `tags =`.
*   **Exclusions:** Data sources, resources that do not support tags (e.g., `aws_security_group_rule` in older providers).

### 2. Execution Logic (Per Resource)

**A. Module Contract:**
Ensure the module accepts metadata. Check `variables.tf`.
*   *If missing:* Inject `variable "tags" { type = map(string) description = "Metadata" default = {} }`.

**B. Injection Strategy (Safe Merge):**
Replace resource definition to include merge.

*   *Before:*
    ```hcl
    resource "aws_s3_bucket" "main" {
      bucket = "foo"
    }
    ```
*   *After:*
    ```hcl
    resource "aws_s3_bucket" "main" {
      bucket = "foo"
      tags   = merge(var.tags, {
        Name = "foo"
      })
    }
    ```
*   *Legacy Protection:* If `tags = { ... }` exists, wrap it in `merge(var.tags, { ... })`.

**C. Verification (Module Level):**
Run `terraform validate` in the specific module directory. DO NOT run at root unless initializing fully.

---

## 🔁 Phase 3: Source Code Headers (Future)

**Context:** Not currently enforced by validator. Preparation only.

**Standard Header:**
```python
# -----------------------------------------------------------------------------
# @id: <ID>
# @type: script
# @owner: <owner>
# -----------------------------------------------------------------------------
```

**Action:**
1.  Identify `.py`, `.sh`, `.Dockerfile` inputs.
2.  Prepend Header.
3.  Register ID in `SCRIPT_REGISTRY.md`.
4.  Do not block on validation (Validator update required).

---

## ✅ Final Validation (The Gate)

1.  **Validator Compliance:** `python3 scripts/validate-metadata.py docs --json` -> `failed: 0`.
2.  **Build Safety:** `terraform validate` (Top Level Modules).
3.  **Plan Safety:** `make plan ENV=dev` -> MUST show **0 Destructive Changes**. Tag changes are allowed.
4.  **Index Update:** Run `python3 scripts/check-doc-freshness.py --update` (Pseudo-command) or manually update `DOC_INDEX.md`.

**(End of Runbook)**
