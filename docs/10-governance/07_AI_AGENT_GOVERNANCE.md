# AI Agent Governance

Doc contract:
- Purpose: Define governance rules for AI agents integrated into GoldenPath IDP.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/80-onboarding/26_AI_AGENT_PROTOCOLS.md, docs/10-governance/04_PR_GUARDRAILS.md, docs/90-doc-system/AI_CHANGELOG.md

This policy defines how AI agents are authorized, audited, and validated to
preserve quality and trust in the platform.

## Core principle

AI may accelerate execution, but ownership, authority, and risk acceptance
remain human.

## 1) Scope and authority

- AI agents are contributors, not owners.
- All changes require explicit user approval and must follow PR gates.
- Agents must not merge to `main` directly; use `development` as the source of
  truth unless otherwise approved.
- All merges require explicit human approval.

## 2) Agent classes (tiered authority)

**Tier 0 — Read / Reason**
- Allowed: read repo, summarize docs, explain workflows, propose approaches.
- Disallowed: writing files, opening PRs, executing workflows.
- Use case: exploration and validation.

**Tier 1 — Write, but isolated**
- Allowed: create branches, generate code/docs, open PRs, update metadata,
  draft ADRs/runbooks.
- Required: PR description links to a user story, ADR (or "ADR needed"), and
  affected workflows.
- Disallowed: merge to main, trigger destructive workflows.
- Use case: scaffolding, refactors, documentation, templates.

**Tier 2 — Execute safely**
- Allowed: run tests/linters, terraform plan, render manifests, validate
  policies.
- Required: execution logs attached to PR; no side effects outside ephemeral
  envs.
- Disallowed: apply, destroy, auth/IAM changes.
- Use case: CI assistance and validation loops.

**Tier 3 — High risk (human only)**
- Only humans: terraform apply, destroy/teardown, IAM/auth changes, cluster
  lifecycle actions, policy enforcement changes.
- AI may recommend, but must not execute without explicit instruction.

## 2) Guardrails

- **Branching:** no branch create/switch/delete without explicit approval.
- **Destructive actions:** no resets, deletes, or force-pushes without approval.
- **Change discipline:** prefer Makefile targets and documented workflows.
- **Guardrail alignment:** labels must match actual changes; remove false
  positives to avoid blocking.

## 3) Auditability

- Every AI-driven change must be traceable to a PR or commit.
- Evidence (run logs, CI links, or metrics) must be recorded when available.
- Record AI contributions in `docs/90-doc-system/AI_CHANGELOG.md`.

## 4) QA and accuracy

- No unverified claims: if tests are not run, state it explicitly.
- CI must be green before work is considered complete.
- When errors occur, use the deterministic triage loop:
  read logs → fix → re-run → confirm green.

## 5) Data handling

- Never introduce secrets into the repo.
- Do not copy sensitive data into docs or logs.
- Redact or summarize external logs before adding them to docs.

## 6) Exceptions and escalation

- Emergency overrides require explicit approval in the current turn.
- If a change could impact infrastructure, evidence is mandatory.

## 7) Responsibilities

- **Agent:** execute safely, document decisions, and provide evidence.
- **Operator:** approve scope, review changes, and validate outcomes.
