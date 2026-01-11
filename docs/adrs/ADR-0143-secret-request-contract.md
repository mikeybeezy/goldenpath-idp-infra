# ADR-0143: Standardization of the SecretRequest Interface

## Status
Proposed

## Decision
We designate kind: SecretRequest as the primary interface for managing sensitive data. This contract binds AWS Secrets Manager, ESO, and IAM into a single simplified request.

## Specification (Simplified)
- Metadata: id, name, service, environment, owner.
- Spec: provider, rotation, risk-tier, approvals.

## Compliance
- All SecretRequest files must be stored in gitops/catalog/secrets/.
- Must satisfy the PR_GUARDRAILS.py.
