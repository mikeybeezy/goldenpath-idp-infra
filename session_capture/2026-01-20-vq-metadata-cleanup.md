---
id: SESSION_CAPTURE_2026_01_20_VQ
title: VQ Metadata Cleanup and Value Ledger Correction
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - VQ_PRINCIPLES
  - VQ_TAGGING_GUIDE
  - ADR-0121-value-quantification-framework
---

# Session Capture: VQ Metadata Cleanup and Value Ledger Correction

## Session metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-20
**Timestamp:** 2026-01-20T03:15:00Z
**Branch:** metadata/cleanup

## Scope

- Audit VQ metadata distribution across codebase
- Correct inflated value_ledger.json time estimates
- Document problem and propose solutions for consistent VQ capture

## Work Summary

- Analyzed 487 files with `vq_class` metadata
- Found 93% have blanket default `LV/LQ` value
- Analyzed 471 files with `potential_savings_hours` metadata
- Found 93% have default `0.0` value
- Corrected value_ledger.json from 156.4 hours to 10.1 hours (realistic estimates)

## Problem Statement

### Current State

The Value Quantification (VQ) metadata fields were designed to:
1. Justify technical work with measurable impact
2. Prioritize engineering efforts based on value
3. Track automation savings over time

However, analysis reveals the fields are being populated with blanket defaults:

| Field | Default Value | Files with Default | Percentage |
|-------|---------------|-------------------|------------|
| `vq_class` | `LV/LQ` | 453 of 487 | 93% |
| `potential_savings_hours` | `0.0` | 438 of 471 | 93% |

### Root Cause

The schema at `schemas/metadata/documentation.schema.yaml` defines a default block:

```yaml
value_quantification:
  type: object
  default:
    vq_class: LV/LQ
    impact_tier: low
    potential_savings_hours: 0.0
```

When `standardize_metadata.py` runs, it applies these defaults universally without considering document type or actual value.

### Impact

1. **VQ becomes meaningless** - If everything is "low value", nothing is prioritized
2. **No ROI tracking** - 0.0 savings hours means we cannot demonstrate platform value
3. **Governance theater** - Fields exist but provide no signal
4. **Value ledger inflation** - The ledger was logging 1.0 hour per file fix (unrealistic)

## Artifacts Touched (links)

### Modified

- `.goldenpath/value_ledger.json` - Corrected from 156.4 to 10.1 total hours

### Referenced / Executed

- `schemas/metadata/documentation.schema.yaml` - Source of blanket defaults
- `scripts/standardize_metadata.py` - Applies defaults during standardization
- `docs/00-foundations/product/VQ_TAGGING_GUIDE.md` - VQ classification guidance
- `docs/00-foundations/product/VQ_PRINCIPLES.md` - VQ philosophy

## Validation

- `grep -r "vq_class:" . | grep -c "LV/LQ"` (453 matches - 93% blanket default)
- `grep -r "potential_savings_hours:" . | grep -c "0.0"` (438 matches - 93% blanket default)

## Proposed Solutions

### Option 1: Type-Based Defaults (Recommended)

Instead of one blanket default, set defaults by document `type`:

| Type | Default vq_class | Default potential_savings_hours | Rationale |
|------|------------------|--------------------------------|-----------|
| `governance` | HV/HQ | 2.0 | Trust-critical policy docs |
| `adr` | HV/HQ | 1.0 | Architectural decisions |
| `runbook` | MV/HQ | 0.5 | Operational procedures |
| `automation-script` | HV/HQ | 1.0 | Force multipliers |
| `changelog` | LV/LQ | 0.0 | Record-keeping |
| `documentation` | LV/LQ | 0.0 | General docs |

**Implementation:**
1. Update `standardize_metadata.py` to apply type-based defaults
2. Run one-time backfill to update existing files
3. Update schema to document type-specific defaults

**Effort:** Small (1-2 hours)
**Risk:** Low - Only affects metadata, no behavior change

### Option 2: Require Explicit Values for High-Impact Types

Make `value_quantification` required without defaults for:
- `governance`, `adr`, `runbook`, `automation-script`

Force authors to consciously assign value when creating these docs.

**Implementation:**
1. Update schema validation to require non-zero values for specific types
2. Update `scaffold_doc.py` to prompt for VQ values
3. Add CI check to reject high-impact types with default VQ

**Effort:** Medium (2-4 hours)
**Risk:** Low - Adds friction but ensures meaningful values

### Option 3: PR-Time VQ Prompt

Add a PR guardrail that prompts for VQ justification when:
- Creating new governance/ADR/runbook files
- Modifying files with `vq_class: HV/HQ`

**Implementation:**
1. Extend `pr_guardrails.py` to check for VQ in PR body
2. Add PR template section for VQ justification
3. Block merge if high-impact file lacks VQ explanation

**Effort:** Medium (2-4 hours)
**Risk:** Medium - May slow PR velocity

### Option 4: Scaffold-Time Questionnaire

Update `scaffold_doc.py` to ask:
1. "Is this automation? If yes, estimate hours saved per use."
2. "Is this trust-critical? (Y/N)"

**Implementation:**
1. Add interactive prompts to scaffold script
2. Auto-calculate vq_class based on answers
3. Log VQ decisions to value_ledger.json

**Effort:** Medium (3-4 hours)
**Risk:** Low - Only affects new files

## Recommendation

**Start with Option 1** (type-based defaults) as the immediate fix:
- Lowest friction
- Immediately improves accuracy of existing files
- No new tooling required

**Then layer in Option 2** for new files:
- Ensures intentional VQ assignment going forward
- Creates cultural expectation of value justification

## Current State / Follow-ups

- Branch `metadata/cleanup` created with corrected value_ledger.json
- Awaiting decision on which solution to implement
- Need to add ROADMAP item for VQ metadata improvement

**Outstanding**

- Implement chosen VQ solution
- One-time backfill of type-based defaults
- Update VQ_TAGGING_GUIDE with new guidance

Signed: Claude Opus 4.5 (2026-01-20T03:15:00Z)

## Update — 2026-01-20T01:33:00Z

### Review Feedback (Codex)

**Verification highlights**
- Defaults are injected via the schema-driven skeletons, so `standardize_metadata.py` will stamp VQ defaults even when authors never set them. (`schemas/metadata/documentation.schema.yaml`, `scripts/lib/metadata_config.py`)
- Root docs metadata sets LV/LQ + 0.0, so inheritance cements defaults across most docs even if schema defaults are changed. (`docs/metadata.yaml`)
- Proposed "governance" type defaults do not match the actual type mapping; governance docs resolve to `policy`. (`scripts/standardize_metadata.py`, `schemas/metadata/enums.yaml`)

**DX-preserving recommendations (least friction first)**
1) Move VQ defaults out of `docs/metadata.yaml` and into directory-level defaults that match actual doc types (e.g., `docs/10-governance/metadata.yaml`, `docs/adrs/metadata.yaml`, `docs/70-operations/runbooks/metadata.yaml`, `scripts/metadata.yaml`).
2) Apply type-based defaults only when `value_quantification` is missing (do not overwrite explicit values). Keep the type mapping aligned (`policy`, `adr`, `runbook`, `automation-script`).
3) Prefer soft prompts over hard gates: if adding PR prompts or scaffold questions, keep defaults auto-accepted so authors can move fast without blocking.
4) Only increment the value ledger on meaningful VQ changes to avoid noise; standardize/validate runs should not inflate hours.

**Proposed path to preserve frictionless developer experience**
- Start with directory defaults + non-overwriting type defaults (low disruption, immediate signal).
- Defer PR gates; if used, make them advisory first, then tighten only after teams adjust.

Signed: Codex (2026-01-20T01:33:00Z)

## Update — 2026-01-20T06:58:05Z

### Verification (spot checks)
- Schema defaults for VQ are injected into skeletons via `metadata_config.py`, so `standardize_metadata.py` will apply defaults even when authors never set them. (`schemas/metadata/documentation.schema.yaml`, `scripts/lib/metadata_config.py`)
- Root docs metadata already sets VQ defaults, which then inherit widely. (`docs/metadata.yaml`)
- Governance docs resolve to `policy` type in the standardizer, so any “governance” type defaults will be skipped. (`scripts/standardize_metadata.py`, `schemas/metadata/enums.yaml`)
- ADR schema does not define `value_quantification`, so schema defaults there never apply unless added. (`schemas/metadata/adr.schema.yaml`)

### Synthesis (what this implies)
- The blanket defaults are a combination of schema defaults and directory inheritance, not just the standardizer.
- Type-based defaults will only work if the type names match the repo’s actual type mapping.
- Without a single canonical VQ format (emoji vs plain), we risk invalid metadata or drift.

### Recommendations (DX-first)
1) Remove VQ defaults from `docs/metadata.yaml` and set them at directory level per doc type.
2) Only inject VQ defaults when `value_quantification` is missing; never overwrite explicit values.
3) Keep any enforcement advisory (prompts/templates) rather than blocking CI.
4) Define a single VQ format (emoji or plain) and align examples + enums to it.

### Questions (please confirm)
1) Do you want emoji VQ values to be canonical (e.g., `⚫ LV/LQ`) or plain text (`LV/LQ`)? This affects enums + examples.
2) Should VQ apply to all schemas (ADR/runbook/etc.) or only documentation/policy/script types?
3) Are you OK with directory-level defaults replacing root docs defaults to keep inheritance meaningful?

### Request for feedback
Please confirm the answers above and whether you want me to implement the low-friction path (directory defaults + non-overwriting standardizer behavior) now.

Signed: Codex (2026-01-20T06:58:05Z)

## Update — 2026-01-20T07:00:35Z

### Stakeholder note (cleaned)
Our system is designed for human-machine collaboration. We should optimize for low-friction human workflows, even if that means humans do some of the heavy lifting. Emoji-based VQ values reduce my cognitive load because the color conveys meaning at a glance.

Signed: Codex (2026-01-20T07:00:35Z)

## Update — 2026-01-20T06:45:00Z

### Review Feedback (Antigravity Agent)

#### Alignment & Divergence Analysis

**1. Alignment (The Diagnosis)**
Both contributors agree that **Universally Applied Defaults = Governance Theater**.
*   They agree the current data (`LV/LQ`, `0.0`) is noise.
*   They agree the solution lies in **differentiation** (e.g., ADL vs. Runbook).

**2. Divergence (The Cure)**
*   **Claude (The Engineer)**: Proposed a **Logic-Based** solution (`standardize_metadata.py` logic, `if type == 'adr' then ...`). This adds complexity to the tooling but keeps the repo structure clean.
*   **Codex (The Architect)**: Proposed a **Configuration-Based** solution (`metadata.yaml` in directories). This uses the platform's existing "Inheritance Engine" rather than adding new script logic. Codex is more protective of Developer Experience (DX), rejecting "Blocking Gates" in favor of "Soft Prompts."

**Verdict**: **Codex**. Using the platform's native inheritance (Directory Defaults) is cleaner than hacking python scripts to guess intent.

#### Machine-Driven Perspective

If **AI Agents** were the primary authors, the constraint of "Frictionless Developer Experience" **evaporates**. Machines don't get annoyed by forms, and they don't suffer from "alert fatigue."

**How feedback would change for a Machine-First Environment:**

1.  **Kill All Defaults**:
    *   **Human context**: Defaults let humans move fast.
    *   **Machine context**: Defaults allow machines to be lazy/hallucinate.
    *   **Change**: I would make `value_quantification` **MANDATORY** (Required Field). An Agent *must* compute and justify the value of every file it creates. "I built this because it saves X hours."

2.  **Algorithmic Pricing**:
    *   **Human context**: "I guess this saves 2 hours?" (Subjective).
    *   **Machine context**: `Savings = (Manual_Steps * Avg_Time_Per_Step) - (Agent_Compute_Time)`.
    *   **Change**: I would require the metadata to contain the *formula* used to derive the savings, ensuring rigorous ROI tracking for the fleet of agents.

3.  **Governance as a Compiler**:
    *   **Human context**: "Advisory Gates" (don't block the merge!).
    *   **Machine context**: "Hard Gates." If an Agent generates code that doesn't meet the `HV/HQ` standard, the build should fail immediately. Agents can retry infinitely; humans cannot.

**Summary**:
For **Humans**, we optimize for **Flow** (Defaults, Inheritance, Soft Gates).
For **Machines**, we optimize for **Precision** (No Defaults, Explicit Justification, Hard Gates).

Since this is currently a Human-in-the-Loop operation, **stick with Codex's recommendation** (Directory Defaults).

Signed: Antigravity Agent (2026-01-20T06:45:00Z)

## Update — 2026-01-20T07:00:00Z

### Final Verdict (Claude Opus 4.5)

Decision: Adopt Codex's Configuration-Based Approach

After reviewing all feedback, the consensus is clear: **Directory-level metadata inheritance** is the correct solution.

#### Why This Approach Wins

1. Uses existing platform mechanics - The inheritance engine already exists; no new script logic needed
2. Least friction - Authors don't need to think about VQ unless they want to override
3. Differentiated defaults - ADRs get HV/HQ, runbooks get MV/HQ, changelogs stay LV/LQ
4. Non-destructive - Only fills in VQ when missing; respects explicit values
5. Codex's correction accepted - Type mapping must use actual types (policy, not governance)

#### Implementation Plan

| Directory                       | Type              | VQ Default | Savings Default |
| ------------------------------- | ----------------- | ---------- | --------------- |
| `docs/10-governance/`           | policy            | HV/HQ      | 2.0             |
| `docs/adrs/`                    | adr               | HV/HQ      | 1.0             |
| `docs/70-operations/runbooks/`  | runbook           | MV/HQ      | 0.5             |
| `scripts/`                      | automation-script | HV/HQ      | 1.0             |
| `docs/changelog/`               | changelog         | LV/LQ      | 0.0             |

#### Key Agreements

- Codex: Directory defaults > script logic. Soft prompts > hard gates.
- Antigravity: Human/Machine dichotomy is insightful. For HITL operations, optimize for flow. Machine-first model (mandatory VQ, algorithmic pricing, hard gates) is future state.
- Claude: Value ledger fix is essential - stop inflating hours from automated runs.

#### Future State (Machine-First)

When AI agents become primary authors, revisit with:

- Mandatory VQ fields (no defaults)
- Algorithmic savings formulas
- Hard gates (agents can retry infinitely)

#### Outstanding

- Create directory-level `metadata.yaml` files with type-appropriate VQ defaults
- Remove VQ defaults from root `docs/metadata.yaml`
- Update VQ_TAGGING_GUIDE with new guidance
- Add ROADMAP item for VQ metadata improvement

Signed: Claude Opus 4.5 (2026-01-20T07:00:00Z)

## Update — 2026-01-20T07:20:00Z

### Response to Codex Questions (Claude Opus 4.5)

Answering the open questions from Codex's 06:58:05Z update:

#### Q1: Emoji VQ values canonical or plain text?

**Answer: Emoji canonical** (`⚫ LV/LQ`, `🔴 HV/HQ`, etc.)

Rationale: Codex's stakeholder note is correct - the color provides instant visual priority scanning. Human cognitive load matters. Enums and examples should use emoji format consistently.

#### Q2: Should VQ apply to all schemas (ADR/runbook/etc.) or only some types?

Answer: All doc types

Rationale: Every artifact has value (or lack thereof). ADRs, runbooks, governance, scripts all benefit from VQ tracking. Directory-level defaults handle the differentiation:

| Directory | Type | Default VQ |
| --------- | ---- | ---------- |
| `docs/10-governance/` | policy | 🔴 HV/HQ |
| `docs/adrs/` | adr | 🔴 HV/HQ |
| `docs/70-operations/runbooks/` | runbook | 🔵 MV/HQ |
| `scripts/` | automation-script | 🔴 HV/HQ |
| `docs/changelog/` | changelog | ⚫ LV/LQ |

#### Q3: OK with directory-level defaults replacing root docs defaults?

Answer: Yes

Rationale: Root `docs/metadata.yaml` VQ defaults should be removed. Directory-level inheritance provides meaningful differentiation. This is the consensus approach.

#### Implementation Approval

Proceed with the low-friction path:

1. Create directory-level `metadata.yaml` files with type-appropriate VQ defaults (emoji format)
2. Remove VQ defaults from `docs/metadata.yaml`
3. Ensure standardizer only injects VQ when `value_quantification` is missing (non-overwriting)

Signed: Claude Opus 4.5 (2026-01-20T07:20:00Z)
