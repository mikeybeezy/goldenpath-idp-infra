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
