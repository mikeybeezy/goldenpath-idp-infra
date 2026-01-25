<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: PRD-0003-backstage-plugin-scaffold
title: 'PRD-0003: Backstage Plugin Scaffold (Vanilla Template)'
type: documentation
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - DOCS_PRDS_README
  - EC-0012-backstage-plugin-scaffold
  - ADR-0171-platform-application-packaging-strategy
  - ADR-0172-cd-promotion-strategy-with-approval-gates
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# PRD-0003: Backstage Plugin Scaffold (Vanilla Template)

Status: draft
Owner: platform-team
Date: 2026-01-21

## Problem Statement

We need a repeatable, low-friction way to demonstrate the GoldenPath pipeline
end-to-end and to enable teams to create Backstage plugins consistently. Today,
plugin creation is manual, integration steps are scattered, and the demo path
is not obvious or fast.

## Goals

- Provide a one-click scaffold that produces a working Backstage plugin repo.
- Auto-wire CI, image build, ECR push, GitOps write-back, and Argo deploy.
- Make demo success obvious (visible UI change after commit).

## Non-Goals

- Build a full plugin marketplace or billing system.
- Support production-grade plugin hardening in the first iteration.

## Scope

- Backstage scaffolder template for a vanilla plugin.
- Dev environment deployment by default; staging/prod are optional follow-ons.
- GitOps integration aligned with the current ArgoCD flow.

## Requirements

### Functional

- Scaffolder template creates a repo with plugin UI + minimal backend route.
- CI pipeline builds, tests, and pushes to ECR.
- GitOps write-back updates image tag/digest.
- ArgoCD app or values entry included for deployment.
- Auto-register in Backstage catalog on creation.

### Non-Functional

- Scaffold-to-deploy path should complete in under 30 minutes.
- All versions pinned in the template (no :latest outside dev).
- Secrets handled via existing secrets flow (no new secret formats).

## Proposed Approach (High-Level)

- Create a new scaffolder template backed by a minimal plugin repo skeleton.
- Add CI workflow and GitOps write-back config in the scaffolded repo.
- Provide a standard demo marker (banner/theme toggle) to prove deploy.

## Guardrails

- No production auto-deploy without explicit approval gates.
- Template must not embed credentials or secrets.
- Use least-privilege GitHub App credentials for write-back.

## Observability / Audit

- CI logs for build + publish.
- ArgoCD sync status for deployment.
- Git commit trail for write-back updates.

## Acceptance Criteria

- A new scaffolded plugin deploys to dev and is visible in the browser.
- A code change triggers CI, updates Git, and the UI change is observable.
- Catalog registration is automatic and visible in Backstage.

## Success Metrics

- Median scaffold-to-deploy time < 30 minutes.
- >90% scaffold success rate across three test runs.
- At least two internal teams adopt the template in the first month.

## Open Questions

- Should the scaffold create a new repo or support monorepo workflows?
- Frontend-only vs full-stack plugin defaults?
- Should prod require release tags or pinned SHAs by default?

## References

- EC-0012-backstage-plugin-scaffold
- ADR-0171-platform-application-packaging-strategy
- ADR-0172-cd-promotion-strategy-with-approval-gates

---

## Comments and Feedback
When providing feedback, leave a comment and timestamp your comment.

- <Reviewer name/date>: <comment>
