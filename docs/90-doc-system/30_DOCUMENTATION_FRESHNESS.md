---
id: 30_DOCUMENTATION_FRESHNESS
title: Documentation Freshness Mechanism
type: documentation
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
  - 00_DOC_INDEX
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
status: active
version: '1.0'
dependencies: []
supported_until: 2028-01-01
breaking_change: false
---

# Documentation Freshness Mechanism

Doc contract:

- Purpose: Define how living docs are tracked and reviewed.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/90-doc-system/00_DOC_INDEX.md

This is a living document that defines how GoldenPath keeps critical docs
current, human-friendly, and machine-readable.

## Purpose

- Prevent silent doc drift.
- Keep core platform rules trustworthy.
- Make docs usable by humans and future AI tooling.

## What counts as a living doc

Living docs are the minimal set of documents that must stay accurate to
operate the platform safely. The canonical list is:

`docs/90-doc-system/00_DOC_INDEX.md`

## How freshness is tracked

Each living doc is listed in the index with:

- Owner
- Review cycle (in days)
- Last reviewed date

The index is the single source of truth.

## Validator (mechanism)

A lightweight validator scans the index and reports:

- Missing docs
- Missing metadata
- Overdue reviews

Script:

`scripts/check-doc-freshness.py`

Usage:

```bash
python3 scripts/check-doc-freshness.py
```

Optional strict mode:

```bash
python3 scripts/check-doc-freshness.py --fail
```

Optional subset check:

```bash
python3 scripts/check-doc-freshness.py --fail \
  --only docs/00-foundations/34_PLATFORM_SUCCESS_CHECKLIST.md \
  --only docs/production-readiness-gates/ROADMAP.md
```

Optional pre-due reminder:

```bash
python3 scripts/check-doc-freshness.py --warn-within 7 \
  --only docs/00-foundations/34_PLATFORM_SUCCESS_CHECKLIST.md \
  --only docs/production-readiness-gates/READINESS_CHECKLIST.md
```

Optional test override:

```bash
python3 scripts/check-doc-freshness.py --today 2026-01-01
```

## When to update the date

Update `Last reviewed` when a human review confirms the doc is still correct.
This may coincide with edits or be a separate review pass.

## Non-goals (V1)

- No auto-reset of dates.
- No blocking gates in CI by default.
- No forced review for every PR.

## Future options

- Add a CI warning job that runs the validator.
- Add a required review when platform rail changes occur.
- Add machine-readable tags for AI assistants.

## Production readiness review cadence

The platform runs a 30-day review cycle for:

- docs/00-foundations/34_PLATFORM_SUCCESS_CHECKLIST.md
- docs/production-readiness-gates/ROADMAP.md
- docs/production-readiness-gates/V1_04_CAPABILITY_MATRIX.md
- docs/production-readiness-gates/READINESS_CHECKLIST.md

This is enforced by `.github/workflows/production-readiness-review.yml`.
If you make it a required check on `main`, merges are blocked when the review
is overdue until the docs are checked in and `Last reviewed` is updated.
