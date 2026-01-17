---
id: CL-0063-pr-metadata-auto-heal
title: PR Metadata Auto-Heal and Scoped Validation
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
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
  - ADR-0101
  - CL-0063
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---
# CL-0063: PR Metadata Auto-Heal and Scoped Validation

Optimized the PR metadata validation workflow to reduce friction and improve velocity.

## Changes

### Workflow Updates

#### `.github/workflows/ci-metadata-validation.yml`
- **Scoped Validation**: Now validates only files changed in the PR, not the entire repo
- **Auto-Heal**: Runs `standardize_metadata.py` to fix issues and auto-commits
- **Exempt Labels**: PRs with specific labels bypass validation entirely

### Exempt Labels
| Label | Use Case |
| :--- | :--- |
| `governance-exempt` | General bypass for platform exceptions |
| `buildid` | CI/infrastructure pipeline PRs |
| `docs-only` | Documentation-only changes |
| `typo-fix` | Trivial text corrections |
| `hotfix` | Emergency patches |

## Impact

**Before:**
- Full repo scanned on every PR → slow, unrelated failures
- Manual metadata fixes required → developer friction
- No bypass mechanism → blocked CI pipelines

**After:**
- Only changed files validated → 90% faster
- Auto-heal fixes issues automatically → zero friction
- Exempt labels allow clean CI flow → no blockers

## Verification
```bash
# Create PR with missing metadata
# Observe auto-heal commit in PR
# Verify only changed files were validated
```
