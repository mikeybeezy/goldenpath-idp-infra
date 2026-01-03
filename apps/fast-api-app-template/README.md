# App Template (Reference)

This directory is a reference template for app teams. It bundles the default
manifests needed to deploy an application on the Golden Path.

## Ownership

App-owned (teams edit):
- deployment.yaml
- service.yaml
- servicemonitor.yaml
- dashboards/configmap-dashboard.yaml
- config values inside ingress.yaml (host/path/service/ports)

Platform-owned (teams request changes):
- kong/* (auth plugin, rate limiting, consumers, secrets)
- networkpolicy.yaml (default security posture)
- rbac.yaml (only if the app needs Kubernetes API access)

## Placeholders

Template values use `{{ values.* }}` placeholders rendered by Backstage.
If using manually, replace these placeholders before applying.

## Governance metadata (required)

- `owner_team` (GitHub team slug, e.g., checkout-team)
- `service_tier` (e.g., tier-1, tier-2, tier-3)
- `data_classification` (e.g., public, internal, confidential, restricted)
- `lifecycle` (e.g., experimental, production, deprecated)

## Notes

- Do not manage the same dashboards in both Helm/ConfigMaps and Terraform.
- The ServiceMonitor expects a `release: kube-prometheus-stack` label.
- Living doc: `docs/20-contracts/42_APP_TEMPLATE_LIVING.md`
