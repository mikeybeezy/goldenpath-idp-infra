---
id: session_capture_template
title: Session Capture Template
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
  - session_summary_template
---
# Session Capture Template

## Usage rules

- Append-only once created; do not edit or delete prior entries.
- One file per context-bounded effort (create a new file, do not overwrite older captures).
- Keep timestamps in UTC.
- Add Updates during the session; do not wait until the end.
- Validation entries must match the actual commands executed.
- Consolidate multi-agent feedback into the Review/Validation Appendix to avoid conflicting status.
- Each update should include a short Outstanding block for quick scanning.

## Session metadata

**Agent:** <name>
**Date:** <YYYY-MM-DD>
**Timestamp:** <YYYY-MM-DDTHH:MM:SSZ>
**Branch:** <branch-name>

## Scope

- <bullet>
- <bullet>

## Work Summary

- <bullet>
- <bullet>

## Issues Diagnosed and Fixed

| Issue     | Root Cause        | Fix             |
|-----------|-------------------|-----------------|
| <symptom> | <why it happened> | <what was done> |

## Design Decisions Made

| Decision               | Choice          | Rationale |
|------------------------|-----------------|-----------|
| <what needed deciding> | <option chosen> | <why>     |

## Artifacts Touched (links)

### Modified

- `<path>`

### Added

- `<path>`

### Removed

- `<path>`

### Referenced / Executed

- `<path>`

## Validation

- `<command>` (<result>)

## Current State / Follow-ups

- <bullet>
- <bullet>

Signed: <name> (<timestamp>)

---

## Updates (append as you go)

### Update - <YYYY-MM-DDTHH:MM:SSZ>

**What changed**
- <bullet>

**Issues fixed** (if any)

| Issue | Root Cause | Fix |
|-------|------------|-----|
|       |            |     |

**Artifacts touched**
- `<path>`

**Validation**
- <command + result>

**Next steps**
- <bullet>

**Outstanding**
- <bullet>

Signed: <name> (<timestamp>)

---

## Review/Validation Appendix

### Review Feedback (<reviewer> - <timestamp>)

#### What Works Well

- <bullet>

#### Issues and Gaps

- <bullet>

#### Recommendations

| Priority | Action   | Effort   | Status   |
|----------|----------|----------|----------|
| P0       | <action> | <effort> | <status> |

Signed: <reviewer> (<timestamp>)

### Implementation Update (<implementer> - <timestamp>)

- <bullet>

Signed: <implementer> (<timestamp>)

### Validation Run (<agent> - <timestamp>)

**Scripts executed**

```bash
<command>
```

**Results**

- <bullet>

Signed: <agent> (<timestamp>)
