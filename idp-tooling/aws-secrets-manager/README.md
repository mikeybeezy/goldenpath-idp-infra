---
id: README
title: AWS Secrets Manager Module
type: documentation
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to: []
---

# AWS Secrets Manager Module

This module provisions and manages secrets in AWS Secrets Manager—the system of record for sensitive config. Applications never read from Secrets Manager directly; External Secrets Operator (installed via Helm) syncs the values into Kubernetes namespaces.

Terraform handles:
- Creating secrets and labels per environment.
- Defining IAM policies/rotation schedules.
- Granting platform/tooling components access (e.g., Keycloak admin creds, GitOps deploy keys).

This keeps secrets lifecycle (creation, rotation, access) codified, while Helm/Kubernetes only consumes projected secrets.
