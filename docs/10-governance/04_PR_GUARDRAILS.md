---
id: 04_PR_GUARDRAILS
title: PR Guardrails (GoldenPath IDP)
type: policy
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
- 21_CI_ENVIRONMENT_CONTRACT
- 27_REFACTORING_VALIDATION_GUIDE
- ADR-0044
- ADR-0044-platform-infra-checks-ref-mode
- ADR-0046
- ADR-0046-platform-pr-plan-validation-ownership
- ADR-0063
- ADR-0063-platform-terraform-helm-bootstrap
- CL-0002
- CL-0002-bootstrap-refactor
---

id: 04_PR_GUARDRAILS
title: PR Guardrails (GoldenPath IDP)
type: policy
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
- 01_GOVERNANCE
- 21_CI_ENVIRONMENT_CONTRACT
- 27_REFACTORING_VALIDATION_GUIDE
- 38_BRANCHING_STRATEGY
- ADR-####
- ADR-0044
- ADR-0044-platform-infra-checks-ref-mode
- ADR-0046
- ADR-0046-platform-pr-plan-validation-ownership
- ADR-0063
- ADR-0063-platform-terraform-helm-bootstrap
- CL-####
- CL-0002
- CL-0002-bootstrap-refactor
------

# PR Guardrails (GoldenPath IDP)

Doc contract:

- Purpose: Define PR guardrails, labels, and enforcement workflows.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/40-delivery/38_BRANCHING_STRATEGY.md, docs/10-governance/01_GOVERNANCE.md

This document captures the current PR guardrails, how they are enforced, and
recommended best practices for keeping the platform safe and auditable.

## Scope

Applies to all pull requests targeting `development` or `main`.

## Guardrails in place

### Branch policy gate

- `main` only accepts PRs from `development`.
- Enforced by `/.github/workflows/branch-policy.yml`.

### PR checklist requirements

The PR template requires explicit selections for:

- Change Type
- Decision Impact
- Production Readiness
- Testing / Validation (link + run/command or N/A)
- Risk & Rollback (rollback plan / migration / N/A)

Enforced by `/.github/workflows/pr-guardrails.yml`.

Template enforcement:

- PR bodies must be based on `.github/pull_request_template.md`.
- Guardrails fail if the template header is missing or the body contains
  escaped newlines (`\\n`).

### Auto-labeling by path

PRs are labeled automatically based on touched paths:

- `infra`: envs/modules/bootstrap/gitops/workflows/scripts
- `governance`: docs/10-governance, docs/20-contracts, docs/90-doc-system
- `docs`: remaining docs paths
- `changelog-required`: infra + governance domains
- `adr-required`: modules/bootstrap/gitops/workflows/scripts + governance domains

Configured in `/.github/labeler.yml` and applied by
`/.github/workflows/pr-labeler.yml`.

### Required status checks (branch rulesets)

Ensure branch rulesets for `development` and `main` require these checks:

- `Yamllint`
- `Quality - Super Linter (Markdown)`

Both lint checks run repo-wide to keep YAML and Markdown consistent as the
knowledge graph footprint expands.

### Changelog gate

If `changelog-required` is present, a changelog entry is required:

- `docs/changelog/entries/CL-####-short-title.md`

If `changelog-exempt` is present, the changelog gate is skipped.

Enforced by `/.github/workflows/changelog-policy.yml`.

### ADR gate

If `adr-required` is present, an ADR entry is required:

- `docs/adrs/ADR-####-short-title.md`

Enforced by `/.github/workflows/adr-policy.yml`.

## Testing / Validation guidance

Purpose: make proof visible and consistent.

- Include a plan/apply link when infrastructure changes are touched.
- Provide test commands or workflow run IDs for app/platform changes.
- Use "Not applicable" only when no validation is possible (document why).

## Risk & rollback guidance

Purpose: force explicit acknowledgment of recovery paths.

- Provide rollback notes when changes affect production paths.
- Flag data migrations explicitly (including irreversible changes).
- Use "Not applicable" only when no rollback is necessary.

## Infra plan workflow note

We treat `infra-terraform.yml` as a **manual-only** validation workflow. It is
optional and not required as a gate for PR apply flows. The default plan source
remains the PR plan workflow.

References:

- `docs/adrs/ADR-0046-platform-pr-plan-validation-ownership.md`
- `docs/adrs/ADR-0044-platform-infra-checks-ref-mode.md`
- `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`

## Bootstrap guardrails reference

Bootstrap guardrails and refactors are documented here:

- `docs/adrs/ADR-0063-platform-terraform-helm-bootstrap.md`
- `docs/changelog/entries/CL-0002-bootstrap-refactor.md`
- `docs/40-delivery/27_REFACTORING_VALIDATION_GUIDE.md`

## Best-practice recommendations

- Keep the PR checklist short but mandatory; avoid optional-only sections.
- Require plan/apply links for infra changes to preserve auditability.
- Require a rollback note when touching bootstrap, CI, or infra contracts.
- Auto-label PRs by path and let labels drive ADR/changelog requirements.
- Keep guardrails “thin”: fail fast on missing metadata, not on content quality.

## Main branch hard-lock (required)

Use branch rulesets to enforce the development-only path:

- Require PRs (no direct pushes) to `main`.
- Require the `enforce-development-only` check.
- Require at least one human approval.
- Block force-pushes and deletions.
- Optional: require linear history to avoid drift.
- Exception: allow build-id branches (`build-<dd-mm-yy-NN>` or `build/<dd-mm-yy-NN>`) to merge to `main` for build validation.

## Future options (not enabled)

- Require PR reviews on `main` (adds approval gate, prevents self-merge).
- Enforce CODEOWNERS for infra/governance paths.
