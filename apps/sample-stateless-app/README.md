---
id: APPS_SAMPLE-STATELESS-APP_README
title: Sample Stateless App (Reference)
type: documentation
category: apps
version: 1.0
owner: platform-team
status: active
dependencies:
- chart:helm
- module:kubernetes
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
- FAST_API_APP_TEMPLATE
- 42_APP_TEMPLATE_LIVING
- 18_BACKSTAGE_MVP
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
