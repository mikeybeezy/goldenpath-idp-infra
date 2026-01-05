---
id: ADR-0015-platform-aws-oidc-for-github-actions
title: 'ADR-0015: Use AWS OIDC for GitHub Actions authentication'
type: adr
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2027-01-03
  breaking_change: false
relates_to:
  - ADR-0015
---

# ADR-0015: Use AWS OIDC for GitHub Actions authentication

- **Status:** Proposed
- **Date:** 2025-12-26
- **Owners:** platform team
- **Domain:** Platform
- **Decision type:** Security
- **Related:** `.github/workflows/infra-terraform.yml`, [GitHub OIDC in AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws), [Authenticate GitHub Actions with AWS Using OIDC — No Secrets Needed](https://www.youtube.com/watch?v=Sdzd4N6L5Hg)

---

## Context

GitHub Actions currently needs AWS credentials to run infrastructure workflows. Long-lived access
keys stored as GitHub secrets increase the risk of leakage and require rotation. We want a safer,
auditable, short-lived authentication mechanism aligned with least-privilege access.

---

## Decision

> We will authenticate GitHub Actions to AWS using OIDC (OpenID Connect) and IAM role
> assumption, and stop using long-lived AWS access keys in repository secrets.

Workflows will request a short-lived OIDC token from GitHub and assume a dedicated IAM role via
`sts:AssumeRoleWithWebIdentity`.

---

## Scope

Applies to all GitHub Actions workflows that interact with AWS resources in this repository.

---

## Consequences

### Positive

- No long-lived AWS keys stored in GitHub secrets.
- Short-lived, automatically rotated credentials per workflow run.
- Fine-grained access controls via IAM role policies and conditions (repo, branch, environment).
- Improved auditability in AWS for workflow identity.

### Tradeoffs / Risks

- Requires OIDC provider configuration and IAM role setup in AWS.
- Misconfigured trust policies can block CI or over-grant access.
- Slightly more complex initial setup and documentation.

### Operational impact

- Platform team owns OIDC provider and IAM role configuration.
- Workflows must be updated to use OIDC-based AWS authentication.

---

## Alternatives considered

- Long-lived access keys in GitHub secrets (rejected: higher leak/rotation risk).
- Self-hosted runners with instance profiles (rejected for now: higher ops overhead).

---

## Follow-ups

- Create or verify AWS OIDC provider for GitHub Actions.
- Define IAM roles and least-privilege policies per environment.
- Update workflows to use `aws-actions/configure-aws-credentials` with OIDC.

---

## Notes

If multi-account or multi-env setups expand, consider separate IAM roles and tighter conditions per
environment and branch.
