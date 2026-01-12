---
id: PLATFORM_DASHBOARDS
title: Platform Dashboards
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
  maturity: 1
schema_version: 1
relates_to: []
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
status: active
category: dashboard
---

## 🎯 Platform Dashboards Index

This document serves as the high-integrity map for all operational and strategic dashboards in the GoldenPath IDP.

---

## 🏥 Operational Health

| Dashboard | Location | Purpose |
| :--- | :--- | :--- |
| **Platform Health** | [**`PLATFORM_HEALTH.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/PLATFORM_HEALTH.md) | Real-time compliance, risk, and coverage metrics. |
| **Testing Dashboard** | [**`tests/README.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/tests/README.md) | Unit & Feature test status, and Confidence Matrix ratings. |
| **Registry Catalog** | [**`docs/REGISTRY_CATALOG.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/docs/REGISTRY_CATALOG.md) | Logical inventory of all registries and logical repositories. |

---

## 📈 Value & Strategy

| Dashboard | Location | Purpose |
| :--- | :--- | :--- |
| **Value Quantification** | [**`VQ_TAGGING_GUIDE.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/docs/00-foundations/product/VQ_TAGGING_GUIDE.md) | ROI tracking and value-reclamation principles. |
| **Product Features** | [**`IDP_PRODUCT_FEATURES.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/docs/00-foundations/product/IDP_PRODUCT_FEATURES.md) | Capability ledger and roadmap status. |
| **Governance Pulse** | `bin/governance pulse` | (CLI) Live view of mission alignment and total ROI. |

---

## 🏛️ Governance & Decisions

| Dashboard | Location | Purpose |
| :--- | :--- | :--- |
| **ADR Index** | [**`01_adr_index.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/docs/adrs/01_adr_index.md) | Central log of all architectural decisions. |
| **Changelog Index** | [**`00_index.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/docs/changelog/00_index.md) | Chronological record of all platform changes. |
| **Vocabulary Index** | [**`GOVERNANCE_VOCABULARY.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/docs/10-governance/GOVERNANCE_VOCABULARY.md) | Source of truth for all valid metadata enums. |

---

## 🛠️ Maintenance & Hygiene

| Dashboard | Location | Purpose |
| :--- | :--- | :--- |
| **Friction Report** | [**`FRICTION_REPORT.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/docs/10-governance/FRICTION_REPORT.md) | Log of identified and resolved ecosystem friction. |
| **Certification Matrix** | [**`CONFIDENCE_MATRIX.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/tests/TESTING_STANDARDS.md#maturity-rating-scale) | The five-star rating system for automation. |

---

> [!NOTE]
> All dashboards are generated or updated as part of the standard PR workflow. If a dashboard is out-of-sync, run `bin/governance heal`.
