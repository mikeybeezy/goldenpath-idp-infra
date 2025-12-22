# AWS Secrets Manager Module

This module provisions and manages secrets in AWS Secrets Manager—the system of record for sensitive config. Applications never read from Secrets Manager directly; External Secrets Operator (installed via Helm) syncs the values into Kubernetes namespaces.

Terraform handles:
- Creating secrets and labels per environment.
- Defining IAM policies/rotation schedules.
- Granting platform/tooling components access (e.g., Keycloak admin creds, GitOps deploy keys).

This keeps secrets lifecycle (creation, rotation, access) codified, while Helm/Kubernetes only consumes projected secrets.
