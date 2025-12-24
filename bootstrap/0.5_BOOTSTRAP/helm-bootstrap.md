# Helm Bootstrap Runner (Non-Production)

This document explains what `bootstrap-scripts/helm-bootstrap.sh` does and when to run it.

## Purpose

The runner orchestrates the full bootstrap flow against a fresh EKS cluster. It is intended for:

- Ephemeral eksctl clusters (daily teardown) so tooling comes online immediately.
- Terraform-managed clusters after provisioning completes.
- Local testing environments where you want the same GitOps flow as production.

## What the Script Does

1. Ensures the AWS, kubectl, and helm CLIs are installed.
2. Updates kubeconfig for the target cluster.
3. Runs the prereq checks.
4. Installs Argo CD via Helm.
5. Validates core add-ons (AWS Load Balancer Controller, cert-manager).
6. Applies Argo CD apps (platform tooling and Kong).
7. Runs smoke tests and the audit report.

Argo CD admin access is handled via the dedicated helper script:
`bootstrap/0.5_bootstrap/10_gitops-controller/20_argocd_admin_access.sh`.

## Usage

```sh
./bootstrap-scripts/helm-bootstrap.sh <cluster-name> <region> [kong-namespace]
```

Run this once per cluster after it becomes reachable by kubectl.

## Runner vs individual scripts

Use the runner when you want a clean, repeatable one-shot bootstrap for a new
cluster. It enforces the full sequence and runs the standard checks.

Use individual scripts when you need to rerun or debug a specific step, or
when you are customizing the sequence (for example, skipping Kong until later).

## Suggested Enhancements / Alternatives

- **Terraform integration**: run this after `terraform apply` to standardize platform bring-up.
- **Secrets management**: store Git credentials in a secret manager and inject via CI/CD.
- **Runner hardening**: move to a CI pipeline once the flow is stable.
