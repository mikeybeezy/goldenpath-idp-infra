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

## Roadmap
- Automate group→IAM role sync to reduce manual mapping.
- Document developer tooling for OIDC-based `kubectl` logins (e.g., `kubelogin`).
- Ensure service workloads use IRSA (IAM Roles for Service Accounts) to inherit the same governance principles as human users.
