---
id: 2026-01-06_2145_queryable-intelligence-validation
title: 'Walkthrough: Implementing "Queryable Intelligence" (Enums & Validation)'
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
relates_to: []
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
supported_until: '2028-01-01'
---

# Walkthrough: Implementing "Queryable Intelligence" (Enums & Validation)

We have successfully moved the platform from "Metadata as Documentation" to **"Metadata as Code"** by implementing a unified enum strategy and automated enforcement.

## 🪐 The "Core Contract" (Enums & Schemas)

We established a single source of truth for platform states in the `schemas/` directory.

### [NEW] `enums.yaml`
Centralized list of every allowed value for:
- **Domains** (security, delivery, cost...)
- **Components** (infra, ci, backstage...)
- **Risk Profiles** (none, low, medium, high)
- **Lifecycles** (draft, active, deprecated, archived)

### [NEW] `metadata.schema.yaml`
Defines the **Structural Contract** for all platform artifacts, including:
- Hierarchical inheritance (Directory defaults vs File overrides)
- Standardized relationship edges (`relates_to`, `supersedes`)

---

##  The "Enforcement Engine" (Validation)

We implemented an automated gate to ensure zero drift.

### [NEW] `validate_enums.py`
This script transforms the enums from a text file into an **executable quality gate**.
- **Action**: Scans repository-wide (docs, gitops, envs, idp-tooling).
- **Result**: Blocks any PR that uses values outside the allowed "Queryable Intelligence" set.

---

##  Visibility & Promotion

We've promoted these new capabilities to ensure they are recognized as core platform features.

- **[ADR-0113](file:///Users/mikesablaze/goldenpath-idp-infra/docs/adrs/ADR-0113-platform-queryable-intelligence-enums.md)**: Formalized the architecture decision.  
- **[IDP_PRODUCT_FEATURES.md](file:///Users/mikesablaze/goldenpath-idp-infra/docs/product/IDP_PRODUCT_FEATURES.md)**: Added "Enum Consistency Enforcement" to the Capability Roadmap.  
- **[scripts/index.md](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/index.md)**: Indexed the new validator for easy discovery.

---

##  Professional Standard: Emoji Usage Policy

We've established a strict standard for visual communication to reduce cognitive load while maintaining professional neutrality.

### [NEW] `EMOJI_POLICY.md`
- **Allowed**: Only in instructional docs (READMEs, Runbooks) as semantic markers (⚠️, ✅, 🔒...).
- **Forbidden**: Strictly banned from ADRs, Policies, and Authoritative records.
- **Enforcement**: [`enforce_emoji_policy.py`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/enforce_emoji_policy.py) scans and fixes violations automatically.

---

##  Verification Results

| Test | Status | Note |
| :--- | :--- | :--- |
| **Enum Schema Validation** | ✅ PASS | `enums.yaml` matches platform requirements. |
| **Logic Verification** | ✅ PASS | `validate_enums.py` correctly detects [DRIFT]. |
| **Emoji Cleanup** | ✅ PASS | **106 violations** fixed across 739 files. |
| **Nested Enum Validation** | ✅ PASS | Enhanced engine handles `risk_profile` and `reliability` objects. |
| **Index Sync** | ✅ PASS | ADR Index and Script Index updated. |

---

##  Deep Validation: The Enhanced Engine

We've upgraded the "Governed by Default" logic to support recursive metadata validation.

### [NEW] ADR-0115: Enhanced Enum Validation Engine
- **Dot-Path Support**: Validates nested objects like `risk_profile.security_risk`.
- **CI Injection**: Integrated as a mandatory gate in `ci-metadata-validation.yml`.
- **Flexible Mapping**: Easily extendable for future schema changes.

> [!NOTE]
> This upgrade ensures that even complex governance attributes are strictly managed across the Knowledge Graph.

This work completes the **"Born Governed"** initiative by ensuring that "Governed" means adhering to a strict, queryable standard. 
