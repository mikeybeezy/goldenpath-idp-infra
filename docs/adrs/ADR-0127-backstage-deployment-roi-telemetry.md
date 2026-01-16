---
id: ADR-0127
title: 'ADR-0127: Backstage Helm Deployment with ROI Telemetry'
type: adr
status: accepted
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
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
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
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
