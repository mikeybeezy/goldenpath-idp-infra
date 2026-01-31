---
id: 2026-01-31-ci-validation-deps
title: CI Validation Workflows Lightweight Dependencies Fix
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
  - ci-metadata-validation.yml
---

# CI Validation Workflows Lightweight Dependencies Fix

## Session metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-31
**Timestamp:** 2026-01-31T14:00:00Z
**Branch:** fix/metadata-validation-deps

## Scope

- Fix validation workflows using heavy ML dependencies when only PyYAML is needed
- Prevent 5+ hour hangs in Metadata Validation and other validation workflows

## Work Summary

- Updated 4 validation workflows to use `requirements-ci.txt` instead of `requirements-dev.txt`
- Validation scripts only need PyYAML and stdlib - not PyTorch, CUDA, chromadb, llama-index

## Issues Diagnosed and Fixed

| Issue | Root Cause | Fix |
|-------|------------|-----|
| Metadata Validation hanging 5+ hours | Using `requirements-dev.txt` with heavy ML deps | Use `requirements-ci.txt` |
| EKS/RDS/S3 validation potentially slow | Same issue | Use `requirements-ci.txt` |

## Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Use requirements-ci.txt for validation | Yes | Validation scripts only need PyYAML, not ML packages |

## Artifacts Touched (links)

### Modified

- `.github/workflows/ci-metadata-validation.yml`
- `.github/workflows/ci-eks-request-validation.yml`
- `.github/workflows/ci-rds-request-validation.yml`
- `.github/workflows/ci-s3-request-validation.yml`

### Added

- `session_capture/2026-01-31-ci-validation-deps.md` - This file

### Removed

- None

### Referenced / Executed

- Analyzed import statements in validation scripts to confirm no ML deps needed

## Validation

- CI should complete Metadata Validation in seconds instead of hanging
- `grep -E "^import|^from" scripts/validate_metadata.py` - only needs os, sys, yaml, re

## Current State / Follow-ups

- PR #323 created with fix
- After merge, re-run PR #318 checks - Metadata Validation should pass quickly

Signed: Claude Opus 4.5 (2026-01-31T14:00:00Z)
