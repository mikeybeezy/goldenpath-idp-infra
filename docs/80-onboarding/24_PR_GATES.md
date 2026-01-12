---
id: 24_PR_GATES
title: PR Gates and How to Unblock Them
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
schema_version: 1
relates_to:
  - 00_DOC_INDEX
  - 04_PR_GUARDRAILS
  - 30_DOCUMENTATION_FRESHNESS
  - DOCS_CHANGELOG_README
  - ADR-0101
supersedes: []
superseded_by: []
tags: []
inheritance: {}
status: active
version: '1.0'
supported_until: 2028-01-01
breaking_change: false
category: platform
---

# PR Gates and How to Unblock Them

Doc contract:

- Purpose: Explain PR gates, triggers, and the fastest way to unblock.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/10-governance/04_PR_GUARDRAILS.md, docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md

This is a contributor-facing guide to PR gates. It aims to prevent confusion
by showing what triggers each gate and the expected response. Open to refinement
and contribution.

## Gate flow (approximate)

[PR opened/updated]
        |
        +-------------------------------------------+
        |                                           |
        v                                           v
[Target: development]                       [Target: main]
   (Fast Iteration)                         (Full Compliance)
        |                                           |
        +-----------------------+                   |
        |                       |                   v
        v                       v           [Policy - Branch Policy Guard]
[Quality Checks]        [Policy - Labeler]    - Enforces dev -> main path
  - Pre-commit hooks      - Adds path labels        |
  - YAML/MD Linting             |                   v
        |                       +---------> [Policy - PR Guardrails]
        v                                     - Requires full checklist
[Terraform Plan]                             |
  - (Optional for dev)                       +--> [Policy - ADR Policy]
                                             |
                                             +--> [Policy - Changelog Policy]
                                             |
                                             v
                                     [Quality Checks] (Enforced)
                                       - Doc freshness (index check)
                                       - Metadata validation
```

## Runbook: PR to green (deterministic)

1. Sync base branch and confirm target (`feature -> development`, `development -> main`).
2. Identify required gates from change scope (labels, ADR, changelog, doc freshness).
3. Prepare PR content: short summary, checklist selections, testing notes/links.
4. Add required artifacts (ADR, changelog, doc index updates).
5. Run local guardrails (`bin/governance lint`, `bin/governance audit`).
6. Commit, push, and open PR using `.github/pull_request_template.md` (CLI:
   `gh pr create -F .github/pull_request_template.md`) with checklist completed.
7. Check CI/guardrail results immediately; if any fail, follow the triage loop
   below.
8. Re-run local guardrails (`bin/governance lint`) after fixes and re-push until all checks pass.
9. If checks appear stuck or a retarget is not picked up, add a no-op commit to retrigger.
10. Confirm all required checks are green and approvals are in place.
11. If opening a second PR (for example, `development -> main`), repeat steps 2-10.
12. If GitHub reports merge conflicts, rebase on the base branch and repeat steps 5-10.

## Failure triage loop (repeat until green)

```text
[Check failed] -> read logs -> map to file/rule -> fix -> re-run local checks
     -> push -> re-check CI
```

## When to use a no-op commit

Use a no-op commit only when the PR content has not changed but you need to
force a re-run of checks. Typical cases:

- Retargeted base branch (checks still show the previous branch policy result).
- Workflow or policy checks stuck in "queued" or "in progress".
- GitHub reports a stale or missing check after a force-push or rebase.

Example:

```bash
git commit --allow-empty -m "chore: retrigger PR checks"
git push
```

## Common failures and fast fixes

| Failure | Likely cause | Fast fix |
| --- | --- | --- |
| `trim trailing whitespace` | Extra spaces at line ends | Run `pre-commit run --all-files` and commit changes |
| `end-of-file-fixer` | Missing newline at EOF | Run `pre-commit run --all-files` and commit changes |
| `Missing changelog entry` | `changelog-required` label | Add `docs/changelog/entries/CL-####-short-title.md` |
| `Missing ADR entry` | `adr-required` label | Add `docs/adrs/ADR-####-short-title.md` and update index |
| `Branch Policy Guard` | PR targets `main` from non-`development` | Open PR into `development` |
| `Labeler` | Invalid `.github/labeler.yml` or stale base | Fix config or update base branch |
| Merge conflicts | Base branch moved since branch creation | Rebase on base and resolve conflicts |

| Gate | Target Branch | Trigger | What it checks |
| :--- | :--- | :--- | :--- |
| Policy - PR Labeler | `main` | PR updated | Applies labels from `.github/labeler.yml` |
| Policy - Branch Policy Guard | `main` | PR targets `main` | Only `development` may merge to `main` |
| Policy - PR Guardrails | `main` | PR body | Checklist selections are required |
| Policy - ADR Policy | `main` | `adr-required` | ADR entry exists |
| Policy - Changelog Policy | `main` | `changelog-required` | Changelog entry exists |
| Metadata Validation | `main` | `md/yaml` files | Schema compliance and auto-heal |
| Quality - Pre-commit | **All** | Code changes | Lint/format/hook checks (MD034, MD026, EOF) |
| Quality - YAML/Markdown | **All** | YAML/MD files | Basic syntax linting |
| Quality - Doc Freshness | `main` | Living docs | Doc appears in index and is current |
| Plan - PR Terraform Plan | `main`* | Infra paths | Terraform fmt/validate/plan |

*Note: Infrastructure plans are optional for `development` but recommended for validation.*

## Conditional Bypass Labels (ADR-0101)

Certain labels can bypass PR guardrails if conditions are met:

| Label | Condition | Who Can Use |
| --- | --- | --- |
| `docs-only` | All changed files are `.md` | Anyone |
| `typo-fix` | < 50 lines changed, text files only | Anyone |
| `hotfix` | Target branch is `main` | Platform-team only |
| `build_id` | Terraform files changed | Platform-team only |

Labels are **validated, not trusted**. If the condition is not met, the check fails.

Implemented by: `scripts/pr_guardrails.py`

## Where to look for details

- Guardrails and policy sources: `docs/10-governance/04_PR_GUARDRAILS.md`
- Doc freshness rules: `docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md`
- Changelog policy: `docs/changelog/README.md`

## PR checklist template (copy/paste)

This matches `.github/pull_request_template.md`.

```markdown
Select at least one checkbox per section by changing `[ ]` to `[x]`.

## Change Type
- [ ] Feature
- [ ] Bug fix
- [ ] Infra change
- [ ] Governance / Policy

## Decision Impact
- [ ] Requires ADR
- [ ] Updates existing ADR
- [ ] No architectural impact

## Production Readiness
- [ ] Readiness checklist completed
- [ ] No production impact

## Testing / Validation
- [ ] Plan/apply link provided (paste below)
- [ ] Test command or run ID provided (paste below)
- [ ] Not applicable

Testing/Validation details:
- Plan/apply link:
- Test command/run:

## Risk & Rollback
- [ ] Rollback plan documented (link or notes below)
- [ ] Data migration required
- [ ] No data migration
- [ ] Not applicable

Rollback notes/link:

## Notes / Summary (optional)
-
```

CLI note: prefer `gh pr create -F .github/pull_request_template.md` to avoid
escaped newlines in the PR body.
