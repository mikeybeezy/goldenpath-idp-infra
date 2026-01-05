---
id: PLATFORM_HEALTH
title: Platform Health & Compliance Report
type: documentation
category: governance
status: active
owner: platform-team
version: '2026-01-05'
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
relates_to: []
---

# 🏥 Platform Health Report
**Date Generated**: 2026-01-05 10:14:45
**Total Tracked Resources**: 360
**Metadata Compliance**: 100.0%

## 📊 Lifecycle Distribution
- **Active**: 351
- **Planned**: 1
- **Draft**: 4
- **Deprecated**: 2
- **Accepted**: 2

## 🛡️ Risk Summary (Production Impact)
- **High**: 35
- **Medium**: 28
- **Low**: 296
- **None**: 1

## 📂 Top Categories
- **unknown**: 240
- **gitops**: 20
- **modules**: 16
- **apps**: 11
- **runbooks**: 10

## 🚨 Operational Risks
- **Orphaned Files (No Owner)**: 0
- **Stale Files (Past Lifecycle)**: 0

## 💉 Closed-Loop Injection Coverage
> [!NOTE]
> **How it works**: This metric measures the percentage of 'Governance Sidecars' that have been successfully propagated into live deployment configurations (Helm values, ArgoCD manifests).
- **Coverage**: 100.0% (29/29)