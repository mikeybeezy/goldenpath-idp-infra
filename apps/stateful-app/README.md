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
