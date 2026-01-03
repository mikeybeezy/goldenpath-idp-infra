# ADR-0081: Repo-wide linting for knowledge-graph hygiene

Date: 2026-01-03
Status: Proposed
Owners: platform

## Context

We are introducing a knowledge-graph footprint that relies on consistent YAML
and Markdown. Path-scoped linting misses drift when files move or when new
schemas appear across the repo.

## Decision

Run Markdown and YAML linting repo-wide on every PR and main branch push.
Exclude templated directories that contain non-YAML syntax (for example,
app templates and Helm chart templates) via `.yamllint` ignore patterns.

## Consequences

**Positive**
- Early detection of schema and doc hygiene issues.
- Consistent YAML/Markdown quality as the knowledge graph grows.
- Less reliance on reviewers to catch formatting regressions.

**Negative**
- Initial cleanup effort and stricter CI gate.
- Requires explicit ignores for templated YAML files.

## Alternatives considered

1. **Path-scoped linting only**
   - Rejected: misses drift outside docs/ or workflow paths.
2. **Lint only the knowledge-graph directory**
   - Rejected: does not improve overall repo hygiene and allows related files
     to drift.

## Related

- .github/workflows/super-linter.yml
- .github/workflows/yamllint.yml
- .yamllint
- docs/10-governance/04_PR_GUARDRAILS.md
