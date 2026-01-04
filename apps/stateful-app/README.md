---
id: README
title: Stateful App Template (Reference)
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
