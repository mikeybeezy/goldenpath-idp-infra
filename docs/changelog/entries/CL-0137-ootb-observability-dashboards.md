<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0137
title: 'OOTB Observability: Logs RED & Golden Signals'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to:
  - ADR-0052-platform-kube-prometheus-stack-bundle
  - CL-0137
  - CL-0138-tooling-apps-dashboards
  - PLATFORM_DASHBOARDS
  - agent_session_summary
supersedes: []
superseded_by: []
tags:
  - grafana
  - dashboards
  - observability
inheritance: {}
supported_until: '2028-01-01'
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
date: 2026-01-16
description: Enabled automatic discovery of application dashboards, providing instant
  Golden Signals and Logs RED metrics for all platform services.
---

## Feature: Out-of-the-Box Observability (Golden Signals & RED)

The platform now provides **Zero-Configuration Observability** for all applications. By enabling the Grafana dashboard sidecar and standardizing dashboard ConfigMaps, every service deployed via the Golden Path automatically gets a high-fidelity dashboard without manual setup.

## 🚀 Key Capabilities

### 1. Auto-Discovery Sidecar

- **What changed**: Enabled `sidecar.dashboards` in `kube-prometheus-stack` with `searchNamespace: ALL`.
- **Impact**: Grafana now watches all namespaces for ConfigMaps labeled `grafana_dashboard: "1"`.
- **Value**: Developers just deploy their app, and the dashboard appears instantly.

### 2. Golden Signals (RED Method)

Every application dashboard now standardizes on the **RED** method (Rate, Errors, Duration) out-of-the-box:

- **Rate**: Request Rate (RPS) broken down by method.
- **Errors**: 5xx Error Rate percentage with alerting thresholds.
- **Duration**: P95 Latency histogram.

### 3. Integrated Logs (Logs RED)

- **Log Correlation**: Application logs are correlated directly with metrics in the same view.
- **Error Context**: "Recent Application Logs" panel filters for `error` level logs, providing immediate context for metric spikes.

## Implementation Details

- **Grafana Config**:

  ```yaml
  sidecar:
    dashboards:
      enabled: true
      label: grafana_dashboard
      searchNamespace: ALL
  ```

- **Deployment**: Configured in both `dev` and `local` environments.
- **Verification**: Validated against `Wordpress`, `FastAPI`, and `Stateful` reference architectures.
