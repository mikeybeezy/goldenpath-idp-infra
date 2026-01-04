---
id: PLATFORM_HEALTH
title: Platform Health & Compliance Report
type: documentation
category: governance
status: active
owner: platform-team
version: '2026-01-04'
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
**Date Generated**: 2026-01-04 20:53:51
**Total Tracked Resources**: 324
**Metadata Compliance**: 100.0%

## 📊 Lifecycle Distribution
- **Active**: 321
- **Draft**: 1
- **Deprecated**: 2

## 🛡️ Risk Summary (Production Impact)
- **High**: 27
- **Medium**: 24
- **Low**: 273
- **None**: 0

## 📂 Top Categories
- **unknown**: 228
- **gitops**: 20
- **apps**: 11
- **runbooks**: 10
- **idp-tooling**: 10

## 🚨 Operational Risks
- **Orphaned Files (No Owner)**: 0
- **Stale Files (Past Lifecycle)**: 0

## 💉 Closed-Loop Injection Coverage
> [!NOTE]
> **How it works**: This metric measures the percentage of 'Governance Sidecars' that have been successfully propagated into live deployment configurations (Helm values, ArgoCD manifests).
- **Coverage**: 100.0% (29/29)

## ⚠️ Known Coverage Gaps
While currently tracked resources are 100% compliant, the following areas are currently **untracked** (Dark Infrastructure) and valid targets for future governance phases:
- **Terraform Modules (`envs/**`)**: Currently lack `metadata.yaml` sidecars (relying on AWS tags instead).
- **Automation Scripts (`scripts/*.sh`, `Makefile`)**: Governance headers (In-File) are planned for Phase 3.
