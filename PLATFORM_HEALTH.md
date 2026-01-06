<!-- 🛑 AUTOMATED REPORT - DO NOT EDIT MANUALLY 🛑 -->
---
id: PLATFORM_HEALTH
title: Platform Health & Compliance Report
type: documentation
category: governance
status: active
owner: platform-team
version: '2026-01-06'
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
lifecycle:
  supported_until: '2028-01-01'
  breaking_change: false
relates_to:
  - platform_health.py
---

# 🏥 Platform Health Report
<<<<<<< HEAD
**Date Generated**: 2026-01-06 00:27:33
=======
**Date Generated**: 2026-01-06 00:03:08
>>>>>>> 82a42757eb5968f19d0cc3000abc2ee48ed45cbd
**Total Tracked Resources**: 374
**Metadata Compliance**: 99.2%

## 📊 Lifecycle Distribution
- **Active**: 362
- **Released**: 1
- **Planned**: 1
- **Draft**: 4
- **Deprecated**: 2
- **Accepted**: 4

## 🛡️ Risk Summary (Production Impact)
- **High**: 35
- **Medium**: 28
- **Low**: 308
- **None**: 1

## 📂 Top Categories
- **unknown**: 241
- **gitops**: 20
- **governance**: 16
- **modules**: 16
- **apps**: 11

## 🚨 Operational Risks
- **Orphaned Files (No Owner)**: 0
- **Stale Files (Past Lifecycle)**: 0

## 💉 Closed-Loop Injection Coverage
> [!NOTE]
> **How it works**: This metric measures the percentage of 'Governance Sidecars' that have been successfully propagated into live deployment configurations (Helm values, ArgoCD manifests).
- **Coverage**: 100.0% (29/29)
