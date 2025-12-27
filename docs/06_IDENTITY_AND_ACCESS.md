# Identity & Access Governance

## Purpose

Keycloak is the authoritative source of user identity (groups, SSO), while AWS IAM brokers access to Kubernetes clusters and AWS resources. This document explains how they integrate and the guardrails involved.

## Components

- **Keycloak** – manages realms, users, groups, clients. Configured via Terraform in `idp-tooling/keycloak`.
- **AWS IAM** – defines roles and policies that trust Keycloak’s OIDC tokens.
- **EKS Cluster Access** – controlled by the `aws-auth` ConfigMap and Kubernetes RBAC rules.

## Workflow

1. User authenticates with Keycloak (CLI or UI) and obtains an OIDC token with group claims.
2. AWS IAM OIDC provider validates the token and assumes the mapped IAM role.
3. `aws eks update-kubeconfig` (or `kubelogin`) uses that role to interact with the cluster.
4. Permissions inside Kubernetes are granted based on IAM role mappings (cluster-admin, read-only, namespace-scoped, etc.).

## Governance Rules

- All human access flows through Keycloak; no shared IAM users or long-lived credentials.
- IAM roles are defined/deployed via Terraform; changes require PR review.
- `aws-auth` ConfigMap mappings are codified (no manual edits) so RBAC stays auditable.
- Onboarding/offboarding is handled by Keycloak group membership, which drives IAM role assignments.
- Controller access uses IRSA with Terraform-managed IAM roles and service accounts.
- Node access uses SSM Session Manager by default; SSH is break-glass only and must be documented.
- SSH key pairs are user-specific and only required when `enable_ssh_break_glass=true`.
- `ssh_key_name` is the AWS EC2 key pair name (not the local `.pem` file) and can be passed via CLI vars or `TF_VAR_ssh_key_name` in CI.
- AWS Load Balancer Controller uses the `aws-load-balancer-controller` service account in `kube-system`.
- Cluster Autoscaler IRSA role and service account are created by Terraform with the annotation applied in-cluster.
- EKS OIDC provider is created by Terraform to enable IRSA for controllers.

## Service Accounts in Use (V1)

These service accounts are created by Terraform and annotated for IRSA.

| Service | Namespace | Service Account | IAM Role | Purpose |
| --- | --- | --- | --- | --- |
| AWS Load Balancer Controller | `kube-system` | `aws-load-balancer-controller` | `goldenpath-idp-aws-load-balancer-controller` | Creates/updates AWS load balancers and target groups. |
| Cluster Autoscaler | `kube-system` | `cluster-autoscaler` | `goldenpath-idp-cluster-autoscaler` | Scales node groups based on pending pods. |

## Storage add-ons (when enabled)

When EBS/EFS/snapshot add-ons are enabled, each controller gets its own service
account and (where required) its own IRSA role. We do not share controller
roles across add-ons.

Expected service accounts:

- **EBS CSI** controller (IRSA required)
- **EFS CSI** controller (IRSA required)
- **Snapshot controller** (typically no AWS API access; IRSA only if needed)

## Why Terraform needs a Kubernetes provider

We use the Kubernetes provider to create in‑cluster resources (service accounts)
that must be tightly coupled to AWS IAM roles created by Terraform. This keeps
IRSA bindings auditable and prevents drift between IAM and Kubernetes objects.

## Third‑party app access model

Every third‑party app that needs AWS access must have its own service account
and least‑privilege IAM role. We do not share controller roles across apps.

Creation flow (V1):

1. Create IAM role + policy in Terraform.
2. Create Kubernetes service account with the IRSA annotation.
3. Deploy the app via Argo CD using that service account.

This keeps access scoped, reviewable, and repeatable across environments.

## SSM Session Manager (node access)

SSM Session Manager provides shell access to instances without SSH keys or inbound
port 22. Access is controlled by IAM policies and session activity can be logged.

Why we use it:

- No public SSH exposure.
- Centralized IAM access control.
- Audit trails for sessions.

Example:

```text

aws ssm start-session --target <instance-id>

```text

## Roadmap

- Automate group→IAM role sync to reduce manual mapping.
- Document developer tooling for OIDC-based `kubectl` logins (e.g., `kubelogin`).
- Ensure service workloads use IRSA (IAM Roles for Service Accounts) to inherit the same governance principles as human users.
