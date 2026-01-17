---
id: SESSION_CAPTURE_2026_01_17
title: Session Capture - RDS Guardrails and Relationship Refresh
type: documentation
owner: platform-team
status: active
created: 2026-01-17
reviewer: codex
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---

# Session Capture - RDS Guardrails and Relationship Refresh

**Agent:** Codex
**Date:** 2026-01-17
**Timestamp:** 2026-01-17T09:11:49Z

## Scope

- RDS guardrails, schema validation, and related documentation.
- Session summary formalization and capture workflow.
- Relationship extraction normalization and system map regeneration.

## Work Summary

- Added RDS request schema validation in CI and documented non-manual request guidance.
- Switched RDS guardrails to warn-only during rollout; documented non-dev approval gate.
- Added RDS provisioning toggles/options to runbooks.
- Standardized session summary location and added feedback pointers + artifact tracking.
- Expanded relationship extraction to include session summaries and normalized `relates_to` entries.
- Regenerated the platform system map and refreshed relationship metadata.

## Artifacts Touched (links)

- `.github/workflows/ci-rds-request-validation.yml`
- `.github/workflows/rds-size-approval-guard.yml`
- `.github/workflows/rds-tfvars-drift-guard.yml`
- `schemas/requests/rds.schema.yaml`
- `docs/85-how-it-works/self-service/RDS_DUAL_MODE_AUTOMATION.md`
- `docs/85-how-it-works/self-service/RDS_REQUEST_FLOW.md`
- `docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md`
- `docs/70-operations/runbooks/RB-0031-idp-stack-deployment.md`
- `docs/70-operations/runbooks/RB-0032-rds-user-provision.md`
- `session_summary/agent_session_summary.md`
- `session_summary/session_summary_template.md`
- `session_capture/2026-01-17-rds-session-feedback.md`
- `scripts/extract_relationships.py`
- `scripts/generate_doc_system_map.py`
- `docs/90-doc-system/PLATFORM_SYSTEM_MAP.md`
- `docs/00-foundations/product/CAPABILITY_LEDGER.md`
- `docs/00-foundations/product/FEATURES.md`
- `docs/changelog/entries/CL-0126-ci-governance-registry-fetch.md`

## Validation

- `python3 scripts/validate_metadata.py docs` (pass)

## Current State / Follow-ups

- Relationship refresh rerun after extractor normalization; changes pending commit.
- `.goldenpath/value_ledger.json` updated from validation heartbeat.

Signed: Codex (2026-01-17T09:11:49Z)

---

## Review Feedback: `scripts/extract_relationships.py`

**Reviewer:** Claude Opus 4.5 (claude-opus-4-5-20251101)
**Timestamp:** 2026-01-17T01:15:00Z

### What Works Well

| Capability                            | Status | Notes                                              |
| ------------------------------------- | ------ | -------------------------------------------------- |
| ADR/CL/PRD pattern matching           | ✅      | Finds `ADR-0158`, `CL-0042`, etc.                  |
| Short ID → Full ID resolution         | ✅      | `ADR-0006` → `ADR-0006-platform-secrets-strategy`  |
| Markdown link resolution              | ✅      | Handles relative `../` and absolute `docs/` paths  |
| Inline backtick refs                  | ✅      | Extracts `` `docs/.../*.md` ``                     |
| Self-reference removal                | ✅      | Won't add a doc to its own relates_to              |
| Dry-run mode                          | ✅      | Safe testing before writes                         |
| Normalization of existing relates_to  | ✅      | Cleans up short IDs to full IDs                    |

### Issues and Gaps

#### 1. Missing Reference Patterns

The script doesn't extract:

| Pattern                               | Example                            | Impact                                                                       |
| ------------------------------------- | ---------------------------------- | ---------------------------------------------------------------------------- |
| YAML `relates_to:` in non-frontmatter | Schema files like `rds.schema.yaml`| Won't link schema ↔ ADRs                                                     |
| Workflow `# Relates-To:` comments     | `.github/workflows/*.yml`          | Won't link workflows ↔ docs                                                  |
| `Relates-To:` in frontmatter headers  | Session capture files              | Already in frontmatter, but body references missed                           |
| Runbook references (`RB-XXXX`)        | `RB-0031`, `RB-0032`               | `SHORT_ID_PREFIXES` has `RB` but body pattern only catches `ADR-` and `CL-`  |

**Fix**: Add patterns:

```python
# Pattern: RB/PRD mentions (currently only ADR/CL)
rb_mentions = re.findall(r'\b(RB-\d{4})\b', content)
prd_mentions = re.findall(r'\b(PRD-\d{4})\b', content)
```

#### 2. Non-Markdown Files Ignored

The script only processes `*.md` files, missing:

- `schemas/requests/*.yaml` (contains `relates_to` and references ADRs)
- `.github/workflows/*.yml` (contains `# Relates-To:` comments)
- `scripts/*.py` (docstrings reference ADRs)

**Impact**: Bidirectional metadata only works within markdown. A workflow referencing an ADR won't create a backlink.

#### 3. No Reverse Population (Bidirectional Gap) - CRITICAL

The script extracts references FROM a document but doesn't add backlinks TO referenced documents.

Example:

- `ADR-0158` mentions `ADR-0006` → Script adds `ADR-0006` to ADR-0158's `relates_to`
- But `ADR-0006` doesn't get `ADR-0158` added to its `relates_to`

**This is the main gap for bidirectional metadata.**

**Fix**: Two-pass approach:

```python
# Pass 1: Extract all references
graph = {}  # doc_id -> set of referenced doc_ids

# Pass 2: Invert the graph
for doc_id, refs in graph.items():
    for ref_id in refs:
        if ref_id in all_doc_ids:
            reverse_graph[ref_id].add(doc_id)

# Pass 3: Merge and write
```

#### 4. Duplicate Detection Edge Case

When comparing `current_relates` vs `updated_relates`, if current has mixed short/full IDs, normalizing changes the set even though the references are semantically the same. Currently works correctly (0 updates in dry run when metadata is already normalized).

#### 5. Dependency Extraction Limited

The dependency patterns are narrow and miss:

- `depends_on: ["aws_rds_cluster.main"]` (Terraform)
- `requires: [keycloak, backstage]` (YAML)
- `## Dependencies\n- Keycloak` (markdown sections)

### Recommendations

| Priority | Action                                  | Effort |
| -------- | --------------------------------------- | ------ |
| **P0**   | Add bidirectional backlink population   | Medium |
| **P1**   | Extend to YAML/workflow files           | Medium |
| **P1**   | Add RB/PRD/EC/US pattern extraction     | Low    |
| **P2**   | Add `## Dependencies` section parsing   | Medium |
| **P3**   | Add Terraform `depends_on` parsing      | Low    |

### Accuracy Assessment

#### Markdown-to-markdown relationships: ~85%

- Good at ADR/CL references
- Good at markdown link resolution
- Misses non-prefixed document IDs in prose (e.g., "see PLATFORM_SYSTEM_MAP")

#### Bidirectional completeness: ~50%

- Only populates outgoing references, not incoming backlinks

---

**Signed:** Claude Opus 4.5 (claude-opus-4-5-20251101)
**Timestamp:** 2026-01-17T01:15:00Z
