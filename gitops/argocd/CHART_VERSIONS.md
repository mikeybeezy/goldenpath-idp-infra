---
id: CHART_VERSIONS
title: Helm Chart Versions (Argo-managed)
type: documentation
category: gitops
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

# Helm Chart Versions (Argo-managed)

This file centralizes Helm chart versions for Argo CD apps.

Source of truth: the chart `repoURL` and `targetRevision` in
`gitops/argocd/apps/<env>/*.yaml` (the first item under `sources:`).
When you bump a chart version, update this file in the same PR.

| Chart | Repo | Version (targetRevision) | Envs | Argo app manifests |
| --- | --- | --- | --- | --- |
| cluster-autoscaler | <https://kubernetes.github.io/autoscaler> | 9.43.0 | dev | gitops/argocd/apps/dev/cluster-autoscaler.yaml |
| cert-manager | <https://charts.jetstack.io> | v1.14.4 | dev, test, staging, prod | gitops/argocd/apps/*/cert-manager.yaml |
| fluent-bit | <https://fluent.github.io/helm-charts> | 0.47.0 | dev, test, staging, prod | gitops/argocd/apps/*/fluent-bit.yaml |
| external-secrets | <https://charts.external-secrets.io> | 0.9.13 | dev, test, staging, prod | gitops/argocd/apps/*/external-secrets.yaml |
| datree-admission-webhook | <https://charts.datree.io> | 1.0.12 | dev, test, staging, prod | gitops/argocd/apps/*/datree.yaml |
| loki-stack | <https://grafana.github.io/helm-charts> | 2.9.11 | dev, test, staging, prod | gitops/argocd/apps/*/loki.yaml |
| kube-prometheus-stack | <https://prometheus-community.github.io/helm-charts> | 45.7.1 | dev, test, staging, prod | gitops/argocd/apps/*/kube-prometheus-stack.yaml |
| kong | <https://charts.konghq.com> | 2.47.0 | dev, test, staging, prod | gitops/argocd/apps/*/kong.yaml |
| keycloak | <https://charts.bitnami.com/bitnami> | 22.1.6 | dev, test, staging, prod | gitops/argocd/apps/*/keycloak.yaml |
| backstage | <https://backstage.github.io/charts> | 1.12.0 | dev, test, staging, prod | gitops/argocd/apps/*/backstage.yaml |
