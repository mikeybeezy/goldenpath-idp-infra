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
relates_to:
  - platform_health.py
---

# 🏥 Platform Health Report
**Date Generated**: 2026-01-05 20:05:36
**Total Tracked Resources**: 731
**Metadata Compliance**: 99.6%

## 📊 Lifecycle Distribution
- **Active**: 710
- **Released**: 1
- **Planned**: 2
- **Draft**: 8
- **Deprecated**: 4
- **Accepted**: 6

## 🛡️ Risk Summary (Production Impact)
- **High**: 70
- **Medium**: 56
- **Low**: 601
- **None**: 2

## 📂 Top Categories
- **unknown**: 481
- **gitops**: 40
- **modules**: 32
- **governance**: 22
- **apps**: 22

## 🚨 Operational Risks
- **Orphaned Files (No Owner)**: 0
- **Stale Files (Past Lifecycle)**: 0

## 💉 Closed-Loop Injection Coverage
> [!NOTE]
> **How it works**: This metric measures the percentage of 'Governance Sidecars' that have been successfully propagated into live deployment configurations (Helm values, ArgoCD manifests).
- **Coverage**: 100.0% (29/29)
