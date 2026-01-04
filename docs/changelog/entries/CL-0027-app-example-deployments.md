---
id: CL-0027
title: "CL-0027: App example deployments"
type: changelog
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
  supported_until: 2027-01-04
  breaking_change: false
relates_to: []
---

# CL-0027: App example deployments

Date: 2026-01-03
Owner: platform
Scope: app examples, GitOps templates, documentation
Related: PR #127, docs/adrs/ADR-0075-app-example-deployments.md

## Summary

- add deployable app examples with Helm + Kustomize packaging
- include per-app dashboards and observability scaffolds
- provide Argo CD application manifests per environment
- document deterministic, repeatable deployment pattern

## Impact

- example apps can be deployed via Argo CD with consistent structure
- no runtime impact on existing platform workloads

## Changes

### Added

- `apps/sample-stateless-app` deployable Helm/Kustomize scaffolds
- `apps/stateful-app` StatefulSet + PVC + EFS + ResourceQuota scaffolds
- `apps/Wordpress-on-EFS` deployable example packaging
- `gitops/argocd/apps/<env>/*` example app Applications
- `docs/40-delivery/42_APP_EXAMPLE_DEPLOYMENTS.md` guidance

## Rollback / Recovery

- Remove example app manifests and Argo CD Applications if not needed.

## Validation

- Not run (documentation and template change)
