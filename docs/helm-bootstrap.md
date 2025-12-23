# Helm Bootstrap Script # NON production Only for testin 

This document explains what `bootstrap-scripts/helm-bootstrap.sh` does, when to run it, and options for extending or replacing it.

## Purpose

The script installs Argo CD (default GitOps engine) on a fresh EKS cluster and points it at this repo’s `gitops/` folder so all Helm/Kustomize workloads sync automatically. It is intended for:

- Ephemeral eksctl clusters (daily teardown) so tooling comes online immediately.
- Terraform-managed clusters after provisioning completes.
- Local testing environments where you want the same GitOps flow as production.

## What the Script Does

1. Validates that `kubectl` and `helm` are installed and that your kubeconfig points at the target cluster.
2. Creates an `argocd` namespace (configurable via `ARGO_NAMESPACE`).
3. Installs Argo CD via Helm (`server.service.type=LoadBalancer` so you can reach the UI quickly).
4. Applies an Argo CD `Application` resource that syncs the repository and path specified by:
   - `REPO_URL` (defaults to `git@github.com:your-org/goldenpath-idp-infra.git`)
   - `GIT_PATH` (defaults to `gitops`)
5. Enables automated sync (prune + self-heal) so workloads stay in the desired state.

After the script finishes, retrieve the Argo CD admin password:
```sh
kubectl -n $ARGO_NAMESPACE get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
```

## Usage

```sh
export REPO_URL=git@github.com:your-org/goldenpath-idp-infra.git
export GIT_PATH=gitops
export ARGO_NAMESPACE=argocd
./bootstrap-scripts/helm-bootstrap.sh
```

Run this once per cluster after it becomes reachable by kubectl.

## Suggested Enhancements / Alternatives

- **Argo CD only**: this repo standardizes on Argo CD; Flux is not used.
- **Terraform integration**: wrap the script in a Terraform `null_resource` or use EKS `terraform` outputs (cluster endpoint/role) to automate bootstrap immediately after `terraform apply`.
- **Parameterize chart values**: pass Helm values file via `--values` to customize ingress, SSO, etc., or manage the Argo CD installation itself via GitOps.
- **Use AWS Load Balancer Controller ingress**: change `server.service.type` to `ClusterIP` and expose Argo CD through Kong/ALB for tighter control once the platform is stable.
- **Secrets management**: store `REPO_URL` credentials (SSH deploy key/token) in AWS Secrets Manager and inject via CI/CD instead of exporting locally.

For long-term production, you may prefer to manage Argo CD via Terraform Helm provider or GitOps (self-managing) so even Argo’s installation is declarative. The bootstrap script then becomes a one-time helper rather than a required step.
