# Changelog Guidance (Label-Gated)

This changelog records material, user-visible changes to platform behavior and
contracts. It complements commits, PRs, ADRs, and runbooks by focusing on
observable impact.

## Policy

Changelog entries are required only when a PR carries the label
`changelog-required`. The label is applied when a change affects any item in
the required list below.

## Required when label is set

- CI/CD flow, approvals, or gates
- Terraform behavior or state handling
- Teardown/bootstrap safety or timing
- Defaults, flags, or required inputs
- Operator actions or recovery steps

## Not required

- Comments, formatting, or typos only
- Internal refactors with no behavior change
- Dependency bumps with no user impact

## Entry location and numbering

Entries live in `docs/changelog/entries/` and use sequential IDs that mirror
ADR numbering.

- Format: `CL-0001`, `CL-0002`, ...
- Filename: `CL-0001-short-title.md`
- Sequence is monotonic and never reused

## Template

The canonical template is in `docs/changelog/Changelog-template.md`.
