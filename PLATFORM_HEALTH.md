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
**Date Generated**: 2026-01-06 13:39:31
**Total Tracked Resources**: 388
**Metadata Compliance**: 98.7%

## 📊 Lifecycle Distribution
- **Active**: 365
- **Draft**: 4
- **Superseded**: 6
- **Accepted**: 7
- **Deprecated**: 2
- **Planned**: 1
- **Released**: 1
- **Approved**: 1
- **Passed**: 1

## 🛡️ Risk Summary (Production Impact)
- **High**: 35
- **Medium**: 28
- **Low**: 315
- **None**: 4

## 📂 Top Categories
- **unknown**: 243
- **gitops**: 20
- **governance**: 17
- **modules**: 16
- **apps**: 11

## 🚨 Operational Risks
- **Orphaned Files (No Owner)**: 0
- **Stale Files (Past Lifecycle)**: 0

## 💉 Closed-Loop Injection Coverage
> [!NOTE]
> **How it works**: This metric measures the percentage of 'Governance Sidecars' that have been successfully propagated into live deployment configurations (Helm values, ArgoCD manifests).
- **Coverage**: 100.0% (29/29)
