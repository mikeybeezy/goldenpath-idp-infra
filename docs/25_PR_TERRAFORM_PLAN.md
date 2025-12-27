# PR Terraform Plan (Living Document)

This document describes the PR plan workflow and how it behaves.

## Current behavior

- Trigger: pull requests that touch Terraform files.
- Scope: `envs/dev` only.
- Backend: disabled (`-backend=false`).
- Output: posted as a PR comment.

## Why this exists

- Provide fast, visible infrastructure feedback without Atlantis.
- Keep apply manual and controlled.

## Limitations

- Plan output is truncated if too large.
- Without backend state, plan accuracy can be limited.

## Note

This PR plan uses no backend and no AWS credentials. If you later want higher-fidelity plans, add
read-only AWS OIDC access.

## Change process

- Update the ADR if the workflow changes materially.
- Keep this doc aligned with the workflow file.
