# AI Agent & Operator Protocols

Doc contract:
- Purpose: Define mandatory operating rules for AI agents and collaborators to keep work safe, deterministic, and auditable.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/10-governance/04_PR_GUARDRAILS.md, docs/10-governance/07_AI_AGENT_GOVERNANCE.md, docs/80-onboarding/24_PR_GATES.md, docs/90-doc-system/00_DOC_INDEX.md, docs/90-doc-system/AI_CHANGELOG.md

This doc is the single source of truth for how AI agents and human operators
work inside GoldenPath IDP. It aims to preserve value, prevent drift, and keep
every change explainable and reproducible.

## Scope and roles

**Applies to:** AI agents and human collaborators running tasks in this repo.

**Role focus for agents:**
- Architecture Steward: preserve boundaries, ADRs, and decision quality.
- Reliability Engineer: keep CI/teardown deterministic and measurable.
- Documentation Lead: ensure changes are recorded and linked.

## 1) Governance alignment

This protocol implements the policy in
`docs/10-governance/07_AI_AGENT_GOVERNANCE.md`. When in doubt, follow the
governance doc and request approval.

## 2) Safety and branching (ask-first rule)

- **Branching:** Do not create, switch, or delete branches without explicit
  user approval in the current turn.
- **Dirty state:** Run `git status -sb` before starting work. Never overwrite
  uncommitted manual changes.
- **No rushing:** Do not chain destructive commands without an intermediate
  check-in (for example, delete, reset, force-push).

## 3) The green gate (PRs)

- **Definition of done:** A task is not complete until the PR is green.
- **Failure loop:** If CI fails: read logs → fix the specific issue → re-run
  until green.
- **No false completion:** Do not mark work complete if required checks fail.

Reference:
- PR checklist template: `.github/pull_request_template.md`
- PR gate triage: `docs/80-onboarding/24_PR_GATES.md`

## 4) Documentation triggers (label-gated)

**Changelog** (`docs/changelog/entries/CL-####-short-title.md`)
- Required when `changelog-required` label is present.
- Typical triggers: CI/CD flow changes, Terraform behavior changes, guardrail
  updates.

**ADR** (`docs/adrs/ADR-####-short-title.md`)
- Required when `adr-required` label is present.
- Typical triggers: strategy choices, platform contract changes, security or
  governance shifts.

**Workflow changes**
- Update `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md` when adding or
  changing GitHub Actions.

Rule of thumb: code changes without documentation updates are incomplete when
labels require them.

## 5) Context loading (start of session)

Read and align on priorities before proposing work:
1. `docs/production-readiness-gates/ROADMAP.md`
2. `docs/80-onboarding/13_COLLABORATION_GUIDE.md`

## 6) Standard interfaces

Prefer `Makefile` targets (for example, `make apply`, `make test`) over raw
commands to ensure consistent flags, environment variables, and safety checks.

## 7) Escalation and approvals

- Obtain explicit approval before destructive actions or branch operations.
- If a change could alter infrastructure, validate via the defined CI workflows
  and document the evidence.

## 8) QA and accuracy

- State verification explicitly (tests run vs not run).
- Use evidence links when claiming a change is validated.

## 9) Value preservation mechanisms

These are mandatory habits to preserve agent value and reduce rework:

1. **AI Contribution Ledger**
   - Capture what changed, why, and verification status.
   - Recommended location: `docs/90-doc-system/AI_CHANGELOG.md` (living).

2. **Decision + Evidence Pairing**
   - ADRs and changelog entries must include evidence links (runs, logs, metrics).

3. **Deterministic Runbook Hooks**
   - Every workflow/script change must link to a runbook and a Makefile target.

4. **Guardrail Alignment**
   - Ensure labels match what actually changed; remove false-positive labels to
     prevent incorrect blocking.

5. **Outcome Metrics**
   - Track build time, bootstrap time, teardown time, first-run success rate.
   - Record these in `docs/40-delivery/41_BUILD_RUN_LOG.md`.

## 10) Definition of done

Work is complete when:
- PR is green and merged into `development`.
- Documentation triggers are satisfied (labels honored).
- Evidence links are recorded where required.
