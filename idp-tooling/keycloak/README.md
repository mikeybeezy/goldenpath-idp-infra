---
id: IDP_TOOLING_KEYCLOAK_CONFIG
title: Keycloak Configuration Module
type: documentation
risk_profile:
  production_impact: high
  security_risk: high
  coupling_risk: medium
relates_to:
  - 06_IDENTITY_AND_ACCESS
  - ADR-0005-app-keycloak-as-identity-provider-for-human-sso
  - HELM_KEYCLOAK
version: 1.0
dependencies:
  - provider:keycloak
supported_until: 2028-01-01
breaking_change: false
---
# Keycloak Configuration Module

This module uses the Keycloak Terraform provider to manage *what lives inside* Keycloak after the Helm chart deploys it. Think of the split as:

- **Helm values (`gitops/helm/keycloak/values/*.yaml`)** – deploy the Keycloak application: image, replicas, ingress, admin creds.
- **Terraform config (`idp-tooling/keycloak`)** – codify realms, clients, groups, policies, and defaults so every environment inherits the same SSO contracts.

Keeping the internal configuration in Terraform means:

1. Realms/clients/roles are versioned in Git, not tweaked manually in the UI.
2. Promotion across environments is consistent—`terraform plan/apply` handles differences.
3. Application teams can rely on pre-provisioned clients/secrets as part of the platform contract.

Use this module to define:

- The primary realm(s) for the platform.
- Service clients for Backstage, Kong, Argo CD, etc.
- User groups/roles and their mappings.
- Identity provider settings (GitHub, Google, etc., if needed).

Helm gets Keycloak running; this module keeps its configuration declarative.***
