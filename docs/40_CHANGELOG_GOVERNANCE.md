# Changelog Governance

This document defines how changelog entries are created, reviewed, and
enforced for GoldenPath IDP.

## Purpose

Changelog entries capture material, user-visible changes to platform behavior
and contracts. The changelog is not a commit log.

## Enforcement

- A changelog entry is required only when a PR carries the label
  `changelog-required`.
- CI enforces the label gate and fails when the label is present without a
  corresponding entry.
- The enforcing workflow is `changelog-policy.yml`.

## Required change types

- CI/CD flow, approvals, or gates
- Terraform behavior or state handling
- Teardown/bootstrap safety or timing
- Defaults, flags, or required inputs
- Operator actions or recovery steps

## Exclusions

- Comments, formatting, or typos only
- Internal refactors with no behavior change
- Dependency bumps with no user impact

## Entry format

Entries live in `docs/changelog/entries/` and use sequential IDs:
`CL-0001`, `CL-0002`, ...

Use `docs/changelog/Changelog-template.md` as the canonical template.

## Ownership and review

- The PR author creates the entry when the label is applied.
- Reviewers verify that the entry matches the change impact.

## Related docs

- `docs/changelog/README.md`
- `docs/changelog/CHANGELOG_LABELS.md`
