# Backstage MVP (First App Through CI/CD)

This is the minimal path to prove the platform end‑to‑end: build an app, ship
an image, deploy via GitOps, and expose it through Kong.

## Scope (V1 MVP)

- Minimal Backstage install (catalog + scaffolder + techdocs only).
- CI builds + pushes a single image tag per build.
- GitOps deploys that image via Argo CD.
- Kong routes external traffic to Backstage.

## Checklist

### 1) Scaffold Backstage

- Create the repo with `@backstage/create-app`.
- Keep plugins minimal (catalog, scaffolder, techdocs).
- Add a simple health endpoint in the backend.

### 2) Containerize

- Add Dockerfile and local docker‑compose for dev.
- Use one image tag per build (build ID or git SHA).

### 3) CI build + push

- Build image and push to your registry.
- Emit the image tag as a build output.
- Keep secrets in CI (registry credentials only).

### 4) GitOps deploy

- Add or update an Argo CD app for Backstage:
  - `gitops/argocd/apps/<env>/backstage.yaml`
- Use environment values files:
  - `gitops/helm/backstage/values/<env>.yaml`

### 5) Ingress

- Route through Kong (single external entrypoint).
- Confirm `/` and `/api` are reachable.

### 6) Validate

- Argo CD app shows `Synced/Healthy`.
- Backstage pods are `Ready`.
- Kong route responds (HTTP 200).

## Files to touch (current repo)

- GitOps app: `gitops/argocd/apps/<env>/backstage.yaml`
- Helm values: `gitops/helm/backstage/values/<env>.yaml`
- CI stub: `.github/workflows/ci-backstage.yml`

## Notes

- Auth can remain disabled for MVP; Keycloak is a later integration step.
- Keep the first delivery small so we can validate CI → GitOps → Kong quickly.
