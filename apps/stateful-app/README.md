---
id: APPS_STATEFUL-APP_README
title: Stateful App Template (Reference)
type: template
status: active
domain: delivery
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - FAST_API_APP_TEMPLATE
  - STATEFUL_APP_NAMESPACE
  - STATEFUL_APP_PVC
  - STATEFUL_APP_DEPLOY
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
version: 1.0
dependencies:
  - chart:helm
  - module:efs
  - module:kubernetes
supported_until: 2028-01-01
breaking_change: false
---

# Stateful App Template (Reference)

This directory contains a stateful template scaffold for Golden Path examples
and the original example manifests.

## What is included

- Scaffold templates copied from the fast-api template for consistency.
- Stateful-specific scaffolds:
  - `statefulset.yaml`
  - `pvc.yaml`
  - `resourcequota.yaml`
  - `storageclass-efs.yaml`
  - `pvc-efs.yaml`
- Deployment packaging:
  - `deploy/helm/` for Helm
  - `deploy/kustomize/` for Kustomize

## Notes

- The scaffold templates use `{{ values.* }}` placeholders for Backstage.
- The deployable Helm/Kustomize assets include concrete example values.
