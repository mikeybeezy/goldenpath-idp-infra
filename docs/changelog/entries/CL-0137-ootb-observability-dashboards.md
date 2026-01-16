---
id: CL-0137
title: "OOTB Observability: Logs RED & Golden Signals"
type: changelog
status: active
date: 2026-01-16
domain: platform-core
owner: platform-team
lifecycle: active
schema_version: 1
relates_to:
  - ADR-0052
  - PLATFORM_DASHBOARDS.md
description: Enabled automatic discovery of application dashboards, providing instant Golden Signals and Logs RED metrics for all platform services.
tags:
  - grafana
  - dashboards
  - observability
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

## 📋 Implementation Details

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
