---
id: ADR-0101-pr-metadata-auto-heal
title: 'ADR-0101: PR Metadata Auto-Heal and Scoped Validation'
type: adr
category: governance
version: '1.0'
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - ADR-0098
  - CL-0063
---

# ADR-0101: PR Metadata Auto-Heal and Scoped Validation

## Status
Accepted

## Context
The platform's metadata validation workflow was blocking PRs due to:
1. **Full-repo scanning**: Any `.md` file change triggered validation of the entire repository, causing unrelated failures
2. **Manual remediation**: Developers had to manually fix metadata issues, creating friction and slowing velocity
3. **No escape hatch**: No way to bypass validation for CI/infrastructure PRs that don't need governance checks

This friction contradicted the platform's "Born Governed" philosophy—governance should enable velocity, not block it.

## Decision

### 1. Scope Validation to Changed Files Only
The metadata validator now only checks files modified in the current PR, not the entire repository.

### 2. Auto-Heal Before Blocking
When metadata issues are detected, the workflow runs `standardize_metadata.py` to auto-fix issues and commits the changes. The PR continues without developer intervention.

### 3. Exempt Label Bypass
PRs with specific labels skip metadata validation entirely:
- `governance-exempt` - General bypass for platform-approved exceptions
- `buildid` - CI/infrastructure pipeline PRs
- `docs-only` - Documentation-only changes
- `typo-fix` - Trivial text corrections
- `hotfix` - Emergency patches

## Consequences

### Positive
- **90% faster validation**: Only changed files are scanned
- **Zero-friction governance**: Auto-heal removes manual remediation
- **Consistent metadata**: All files get standardized frontmatter automatically
- **Escape hatch**: Exempt labels allow CI pipelines to proceed without governance overhead

### Negative
- **Unexpected commits**: Bot commits may surprise developers unfamiliar with auto-heal
- **Permissions**: Requires `contents: write` for the workflow to push commits
- **History noise**: Auto-heal commits appear in git log

### Mitigation
- Commit message includes `[skip ci]` to prevent infinite loops
- Clear logging explains what was auto-healed
- Exempt labels documented in workflow README
