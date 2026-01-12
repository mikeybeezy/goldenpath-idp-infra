---
id: CL-0048-automated-platform-health
title: 'CL-0048: Automated Platform Health Auditing'
type: changelog
status: active
owner: platform-team
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
version: '1.0'
lifecycle: active
relates_to:
  - ADR-0090
  - PLATFORM_HEALTH_GUIDE
supported_until: 2027-01-04
breaking_change: false
---

# CL-0048: Automated Platform Health Auditing

## Summary
Integrated the Platform Health Reporter into a continuous automated loop, enabling persistent, repository-native health auditing and "Dark Infrastructure" detection.

## Changes
- **Dashboard Persistence**: Updated `scripts/platform_health.py` to generate and write the root `PLATFORM_HEALTH.md` dashboard.
- **Compliance Hardening**: Enforced the canonical metadata schema (v1.0) on the generated health report.
- **Continuous Update Loop**: Updated `.github/workflows/quality-platform-health.yaml` to automatically commit health updates back to the `development` branch.
- **Injection Coverage**: Added detailed "Closed-Loop Injection Coverage" metrics to track how well metadata is propagated to live resources.

## Business Value
- **Operational Transparency**: Real-time visibility into the platform's governance reach (currently 62.1% injection coverage).
- **Reduced Governance Debt**: Automated detection of orphaned files, missing metadata, and stale lifecycles.
- **Audit-Ready Infrastructure**: The platform now maintains a persistent, historical record of its own compliance state.
