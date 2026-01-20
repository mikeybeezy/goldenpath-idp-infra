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
