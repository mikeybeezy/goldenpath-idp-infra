---
id: ADR-0127
title: 'ADR-0127: Backstage Helm Deployment with ROI Telemetry'
type: adr
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0127
  - RB-0021-backstage-helm-catalog-visibility
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-08
version: 1.0
breaking_change: false
---

## ADR-0127: Backstage Helm Deployment with ROI Telemetry

## Status

Accepted

## Context

We need a deterministic, repeatable method to deploy the Backstage portal while simultaneously quantifying the value (ROI) of our platform automation.

## Decision

We will use a dedicated bash script (`scripts/deploy-backstage.sh`) that encapsulates:

1. **Dependency Management**: Automated installation of the CloudNativePG operator.
2. **Infrastructure Provisioning**: Deployment of the PostgreSQL cluster specifically for Backstage.
3. **Core Configuration**: Deployment of the Backstage Helm chart with GitHub integration.
4. **Value Telemetry**: Integrated call to `vq_logger.py` to record every successful deployment run as a "Value Heartbeat."

## Consequences

- **Automation Advantage**: Reclaims approximately 15 minutes of manual labor per deployment attempt.
- **Reporting Fidelity**: Provides real-time ROI data to the platform leadership dashboard.
- **Governance Alignment**: Every deployment is "Born Governed" with correct metadata and configuration.

---

**Note (2026-01-26):** References to `backstage-helm/` paths in this document are historical. Per CL-0196, the directory structure was consolidated:
- `backstage-helm/charts/backstage/` → `gitops/helm/backstage/chart/`
- `backstage-helm/backstage-catalog/` → `catalog/`
