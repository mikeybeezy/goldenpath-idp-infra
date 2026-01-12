---
id: ADR-0116-emoji-usage-policy-and-enforcement
title: Emoji Usage Policy & Automated Enforcement
type: adr
domain: platform-core
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: none
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle: active
version: 1.0
relates_to:
  - EMOJI_POLICY
  - Quality - Metadata Validation
date: 2026-01-06
supported_until: 2028-01-06
breaking_change: false
---

# ADR-0116: Emoji Usage Policy & Automated Enforcement

## Context
Documentation quality and professional neutrality are core tenets of the platform. Excessive or semi-random emoji usage in authoritative documents (ADRs, Policies, Schemas) can obscure meaning and reduce the professional tone of the repository.

## Decision
We will establish a formal [Emoji Usage Policy](doc/governance/EMOJI_POLICY.md) and implement automated enforcement.

### 1. The Policy
- **Authoritative Documents**: Emojis are strictly prohibited in ADRs, Policies, Contracts, Schemas, and Metadata definitions.
- **Instructional Documents**: Emojis are permitted only for semantic marking (e.g., , , ) to highlight critical information.

### 2. Automated Enforcement
We will use `scripts/enforce_emoji_policy.py` as a Quality Gate:
- **Local Hook**: Integrated into `.pre-commit-config.yaml` to prevent invalid emojis from being committed.
- **CI/CD Gate**: Integrated into `ci-metadata-validation.yml` to block non-compliant PRs.
- **Auto-Healing**: The CI pipeline will automatically strip forbidden emojis from changelogs and documentation when violations are detected.

## Consequences

### Positive
- **Professionalism**: Ensures a consistent, unambiguous tone across the Knowledge Graph.
- **Reduced Cognitive Load**: Semantic emojis highlight important notes without visual clutter.
- **High Integrity**: Automated enforcement prevents policy bypass.

### Negative
- **Strictness**: Developers may occasionally have their commits blocked or auto-healed if they include unapproved emojis.
