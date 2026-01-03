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
