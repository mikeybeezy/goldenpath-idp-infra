---
id: IDP_TOOLING_AWS_SECRETS_MANAGER
title: AWS Secrets Manager Configuration Module
type: documentation
category: idp-tooling
version: 1.0
owner: platform-team
status: active
dependencies:
  - provider:aws
risk_profile:
  production_impact: low
  security_risk: high
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - HELM_EXTERNAL_SECRETS
  - ADR-0006
---

# AWS Secrets Manager Module

This module provisions and manages secrets in AWS Secrets Manager—the system of record for sensitive config. Applications never read from Secrets Manager directly; External Secrets Operator (installed via Helm) syncs the values into Kubernetes namespaces.

Terraform handles:

- Creating secrets and labels per environment.
- Defining IAM policies/rotation schedules.
- Granting platform/tooling components access (e.g., Keycloak admin creds, GitOps deploy keys).

This keeps secrets lifecycle (creation, rotation, access) codified, while Helm/Kubernetes only consumes projected secrets.
