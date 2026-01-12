---
id: IDP_TOOLING_MONITORING_GRAFANA
title: Grafana Configuration Module (In-cluster)
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
schema_version: 1
relates_to:
  - HELM_KUBE_PROMETHEUS_STACK
  - IDP_TOOLING_GRAFANA_CONFIG
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
status: active
version: 1.0
dependencies:
  - chart:kube-prometheus-stack
supported_until: 2028-01-01
breaking_change: false
---

Placeholder for idp-tooling/monitoring-config/grafana
