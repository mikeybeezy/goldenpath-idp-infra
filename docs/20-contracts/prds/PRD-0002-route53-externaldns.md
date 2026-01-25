<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: PRD-0002-route53-externaldns
title: 'PRD-0002: Route53 + ExternalDNS Management'
type: documentation
risk_profile:
  production_impact: medium
  security_risk: medium
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 1
relates_to:
  - DOCS_PRDS_README
  - RB-0033-persistent-cluster-teardown
  - RB-0034-persistent-cluster-deployment
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# PRD-0002: Route53 + ExternalDNS Management

Status: draft
Owner: platform-team
Date: 2026-01-20

## Problem Statement

We need consistent DNS management for platform services (Backstage, Argo CD,
Keycloak) and app workloads. Manual Route53 record management creates drift,
slows bootstrap, and complicates teardown.

## Goals

- Automate DNS record creation and cleanup via ExternalDNS.
- Ensure deterministic bootstrap and teardown sequencing.
- Provide explicit, auditable configuration per environment.

## Non-Goals

- Multi-cloud DNS providers.
- Automated DNS delegation across multiple AWS accounts.
- Auto-provisioning new hosted zones.

## Scope

- Applies to persistent cluster deployments (dev/staging/prod).
- ExternalDNS manages Route53 records for cluster services/ingress.
- Records must be cleaned before cluster teardown.

## Requirements

### Functional

- ExternalDNS can create A/AAAA/CNAME records for defined domains.
- ExternalDNS cleans records when services/ingress are removed.
- Configuration is explicit and environment-scoped.
- Teardown sequence removes ExternalDNS before cluster destruction.
- ExternalDNS uses `sync` policy for env subdomains (authoritative cleanup).

### Non-Functional

- Least-privilege IAM (IRSA preferred).
- No direct edits to Route53 outside documented break-glass.
- Clear audit trail for DNS changes (ExternalDNS logs).

## Proposed Approach (High-Level)

- Add explicit ExternalDNS configuration to env tfvars or Helm values.
- Deploy ExternalDNS after ingress/ALB is ready.
- Remove ExternalDNS (and dependent ingress/services) before teardown.

## Guardrails

- Require explicit enable flag per environment.
- Block teardown if ExternalDNS cleanup is skipped (documentation + runbook).
- Keep Route53 zone IDs immutable per environment.

## Observability / Audit

- ExternalDNS logs enabled and retained.
- Route53 record changes visible via AWS CloudTrail.

## Acceptance Criteria

- Records created for platform services when enabled.
- Records removed when services/ingress are deleted.
- Teardown runbook includes DNS cleanup ordering.

## Success Metrics

- Zero manual Route53 edits for platform services.
- DNS cleanup time under 5 minutes after teardown step.

## Open Questions

- Where should ExternalDNS config live (tfvars vs Helm values)?
- What TXT registry settings should be standard (owner ID, prefix)?
- Do we need multiple hosted zones per environment?

## References

- `docs/70-operations/runbooks/RB-0033-persistent-cluster-teardown.md`
- `docs/70-operations/runbooks/RB-0034-persistent-cluster-deployment.md`
- `docs/20-contracts/prds/PRD-0000-template.md`

---

## Comments and Feedback
When providing feedbackk, leave a comment and timestamop your comment.

- <Reviewer name/date>: <comment>
