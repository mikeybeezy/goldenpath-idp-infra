# Bootstrap Scripts

This folder contains scripts used to bring a fresh cluster to a “GitOps-ready” state. Right now we provide `helm-bootstrap.sh`, which installs Argo CD and points it at this repo’s `gitops/` directory.

For the broader bootstrap flow and directory layout, see `bootstrap/README.md`.

## Argo CD Installation Options (TBD)

We plan to make Argo CD part of every cluster launch, but we’re still deciding **how** to install it by default:

1. **Bootstrap Script** – `helm-bootstrap.sh` installs Argo CD via Helm and seeds a GitOps Application. This is great for ephemeral clusters (e.g., eksctl) where you need the controller up immediately.
2. **Declarative Helm deployment** – `gitops/helm/argocd/` contains Argo CD Helm values consumed by Argo CD Applications. Once Argo CD is running, it manages itself via Git.

We’ll pick one path (or support both) once the platform matures a bit more. Until then:
- Use the script for quick tests or the daily tear-down cluster.
- Use the Helm manifests when you want Argo CD to be managed like any other app.

Future updates to this README will document the final approach once we lock it down.
