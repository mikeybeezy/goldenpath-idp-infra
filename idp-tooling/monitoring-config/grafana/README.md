---
id: IDP_TOOLING_MONITORING_GRAFANA
title: Grafana Configuration Module (In-cluster)
type: documentation
category: idp-tooling
version: 1.0
owner: platform-team
status: active
dependencies:
- chart:kube-prometheus-stack
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
relates_to:
- HELM_KUBE_PROMETHEUS_STACK
- IDP_TOOLING_GRAFANA_CONFIG
---

Placeholder for idp-tooling/monitoring-config/grafana
