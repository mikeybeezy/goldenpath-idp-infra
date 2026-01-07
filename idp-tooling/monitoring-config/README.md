---
id: IDP_TOOLING_MONITORING_CONFIG
title: Monitoring Configuration Overview
type: documentation
relates_to:
  - IDP_TOOLING_MONITORING_ALERTMANAGER
  - IDP_TOOLING_MONITORING_FLUENT_BIT
  - IDP_TOOLING_MONITORING_GRAFANA
version: 1.0
dependencies:
  - chart:kube-prometheus-stack
  - chart:loki
  - chart:fluent-bit
supported_until: 2028-01-01
breaking_change: false
---

# Monitoring Configuration Modules

This directory holds Terraform modules for monitoring components that need API-level configuration beyond Helm:

- `grafana/` – dashboards, datasources, alert rules.
- `alertmanager/` – receivers, routing trees, notification policies.
- `fluent-bit/` – optional configmaps/templates for multi-destination log outputs.
- `loki/` – placeholder for Loki runtime config (retention, limits, auth) if needed.

Helm installs the workloads; these modules describe their internal configuration so alerts, dashboards, and log routing remain declarative across environments.
