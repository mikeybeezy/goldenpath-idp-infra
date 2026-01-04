---

id: README
title: WordPress on EFS (Reference)
type: documentation
category: apps
version: '1.0'
owner: platform-team
status: active
dependencies: []
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
