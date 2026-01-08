---
id: APPS_SAMPLE-STATELESS-APP_README
title: Sample Stateless App (Reference)
type: documentation
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - FAST_API_APP_TEMPLATE
  - 42_APP_TEMPLATE_LIVING
  - 18_BACKSTAGE_MVP
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
  - chart:helm
  - module:kubernetes
supported_until: 2028-01-01
breaking_change: false
---

# Sample Stateless App (Reference)

This directory contains a stateless example app plus scaffold templates that
match the Golden Path app template contract.

## What is included

- Scaffold templates: deployment, service, ingress, ServiceMonitor, RBAC,
  service account, network policy, and dashboard (copied from the fast-api
  template).
- Deployment packaging:
  - `deploy/helm/` for Helm
  - `deploy/kustomize/` for Kustomize

## Notes

- The scaffold templates use `{{ values.* }}` placeholders for Backstage.
- The deployable Helm/Kustomize assets include concrete example values.
- Original example manifests are kept as-is for reference.
