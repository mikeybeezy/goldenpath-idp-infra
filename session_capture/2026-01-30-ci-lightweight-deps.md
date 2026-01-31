---
id: 2026-01-30-ci-lightweight-deps
title: CI Lightweight Dependencies Fix
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
  - session_capture_template
  - python-tests.yml
---

# CI Lightweight Dependencies Fix

## Session metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-30
**Timestamp:** 2026-01-30T23:30:00Z
**Branch:** fix/ci-lightweight-deps

## Scope

- Fix python-tests.yml hanging on dependency install for 5+ hours
- Create lightweight requirements file for CI
- Auto-skip RAG tests when ML deps not installed

## Work Summary

- Created `requirements-ci.txt` with lightweight deps (no PyTorch/CUDA)
- Updated `python-tests.yml` to use lightweight deps
- Created `tests/unit/conftest.py` to auto-skip RAG tests when deps missing

## Issues Diagnosed and Fixed

| Issue | Root Cause | Fix |
|-------|------------|-----|
| CI hanging for 5+ hours | requirements-dev.txt has PyTorch/CUDA via sentence-transformers | Use lightweight requirements-ci.txt |
| RAG tests would fail with ImportError | Missing ML deps in CI | conftest.py auto-skips RAG tests |

## Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Separate CI requirements | Yes | Keeps CI fast, local dev has full deps |
| Auto-skip vs fail | Auto-skip | CI still passes, RAG tests run locally |

## Artifacts Touched (links)

### Modified

- `.github/workflows/python-tests.yml` - Use requirements-ci.txt

### Added

- `requirements-ci.txt` - Lightweight CI dependencies
- `tests/unit/conftest.py` - Auto-skip RAG tests

### Removed

- None

### Referenced / Executed

- `gh pr checks 321` - Monitoring CI

## Validation

- CI should complete in ~3 min instead of hanging
- RAG tests skip with clear message when deps missing

## Current State / Follow-ups

- PR #321 created with fix
- Monitoring CI to confirm fix works
- PR #318 (development → main) blocked until this is merged

Signed: Claude Opus 4.5 (2026-01-30T23:30:00Z)
