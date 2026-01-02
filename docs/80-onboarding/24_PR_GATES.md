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

```text
[PR opened/updated]
        |
        v
[Policy - PR Labeler]
  - Adds labels based on paths
        |
        v
[Policy - Branch Policy Guard]
  - Enforces development -> main rule
        |
        v
[Policy - PR Guardrails]
  - Requires checklist selections
        |
        +--> [Policy - ADR Policy] (if adr-required)
        |       - Add docs/adrs/ADR-####-short-title.md
        |
        +--> [Policy - Changelog Policy] (if changelog-required)
        |       - Add docs/changelog/entries/CL-####-short-title.md
        |
        v
[Quality Checks]
  - Pre-commit hooks
  - Doc freshness (if living docs touched)
  - YAML/Markdown linting (if relevant files)
        |
        v
[Plan - PR Terraform Plan] (infra paths)
  - Terraform fmt/validate/plan
```

## Gate triggers and responses

| Gate | Trigger | What it checks | How to unblock |
| --- | --- | --- | --- |
| Policy - PR Labeler | PR updated | Applies labels from `.github/labeler.yml` | Fix labeler config or update base branch if labeler fails |
| Policy - Branch Policy Guard | PR targets `main` | Only `development` may merge to `main` | Open PR into `development` |
| Policy - PR Guardrails | PR body | Checklist selections are required | Select one option in each required section |
| Policy - ADR Policy | `adr-required` label | ADR entry exists | Add `docs/adrs/ADR-####-short-title.md` |
| Policy - Changelog Policy | `changelog-required` label | Changelog entry exists | Add `docs/changelog/entries/CL-####-short-title.md` |
| Quality - Pre-commit | Code changes | Lint/format/hook checks | Run `pre-commit run --all-files`, fix failures |
| Quality - Doc Freshness | Living docs touched | Doc appears in index and is current | Update `docs/90-doc-system/00_DOC_INDEX.md` |
| Quality - YAML/Markdown | YAML/MD touched | Linting | Fix lint errors |
| Plan - PR Terraform Plan | Infra paths | Terraform fmt/validate/plan | Fix plan errors or re-run after updates |

## Where to look for details

- Guardrails and policy sources: `docs/10-governance/04_PR_GUARDRAILS.md`
- Doc freshness rules: `docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md`
- Changelog policy: `docs/changelog/README.md`

