---
id: CL-0020
title: 'CL-0020: Golden Signals Dashboard Standard'
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
relates_to:

- 09_PLATFORM_DASHBOARD_CATALOG
- ADR-0066
- CL-0020

---

# CL-0020: Golden Signals Dashboard Standard

Date: 2026-01-02
Owner: platform
Scope: apps/fast-api-app-template, gitops/helm/kube-prometheus-stack
Related: docs/adrs/ADR-0066-platform-dashboards-as-code.md, PR #106

## Summary

- Standardized the observability experience by shipping comprehensive Grafana dashboards as code.
- Added "Golden Signals" (RED + Saturation + Logs) to the App Template default.
- Added "Cluster Overview" and "Platform Health" dashboards to the platform stack.

## Impact

- **Developers**: New services created from the template will launch with a full observability dashboard pre-provisioned.
- **Platform Engineers**: Can view Cluster and Addon health immediately in Grafana without manual setup.
- **Workflow**: Dashboards are now immutable artifacts managed by ArgoCD; UI edits will be lost (by design) to enforce GitOps.

## Changes

### Added

- `gitops/helm/kube-prometheus-stack/dashboards/cluster-overview.yaml`: ConfigMap for Cluster Health.
- `gitops/helm/kube-prometheus-stack/dashboards/platform-health.yaml`: ConfigMap for Platform/gitops Health.

### Changed

- `apps/fast-api-app-template/dashboards/configmap-dashboard.yaml`: Replaced empty skeleton with full Golden Signals + Logs model.

### Documented

- `docs/adrs/ADR-0066-platform-dashboards-as-code.md` created.
- `docs/50-observability/09_PLATFORM_DASHBOARD_CATALOG.md` created.

### Known limitations

- Log correlation relies on the `app` label being present on log streams.
- Defaults assume standard Prometheus metrics (`http_requests_total`). Custom instrumentation may require dashboard overrides.

## Rollback / Recovery

- Revert the ConfigMap changes in git to restore previous states (or the empty skeleton).

## Validation

- Validated by inspecting the generated JSON models against Grafana schema.
- Verified PromQL queries against standard `kube-prometheus-stack` metric names.
