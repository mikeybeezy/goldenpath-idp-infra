---
id: APPS_WORDPRESS-ON-EFS_README
title: WordPress on EFS (Reference)
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
relates_to: []
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
version: '1.0'
supported_until: 2028-01-01
breaking_change: false
---

# WordPress on EFS (Reference)

This directory contains a WordPress-on-EFS example with Golden Path scaffolds
and deployable Helm/Kustomize assets.

## What is included

- Scaffold templates copied from the fast-api template for consistency.
- Example docs retained in this folder.
- Deployment packaging:
  - `deploy/helm/` for Helm
  - `deploy/kustomize/` for Kustomize

## Notes

- The scaffold templates use `{{ values.* }}` placeholders for Backstage.
- The deployable Helm/Kustomize assets include concrete example values.
