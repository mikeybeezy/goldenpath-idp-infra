# Changelog: repo-wide linting for knowledge graph hygiene

Date: 2026-01-03
Owner: platform

## Summary

- Run Super Linter (Markdown) on all PRs and main pushes.
- Run Yamllint repo-wide for `.yml` and `.yaml` files.
- Add ignore list for generated and vendor directories.

## References

- Workflow: .github/workflows/super-linter.yml
- Workflow: .github/workflows/yamllint.yml
- Config: .yamllint
- Docs: docs/10-governance/04_PR_GUARDRAILS.md
