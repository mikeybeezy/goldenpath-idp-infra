---
id: README
title: Monitoring Configuration Modules
type: documentation
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to: []
---

# Monitoring Configuration Modules

This directory holds Terraform modules for monitoring components that need API-level configuration beyond Helm:

- `grafana/` – dashboards, datasources, alert rules.
- `alertmanager/` – receivers, routing trees, notification policies.
- `fluent-bit/` – optional configmaps/templates for multi-destination log outputs.
- `loki/` – placeholder for Loki runtime config (retention, limits, auth) if needed.

Helm installs the workloads; these modules describe their internal configuration so alerts, dashboards, and log routing remain declarative across environments.
