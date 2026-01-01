# CI Image Scanning (Living Document)

This document describes the default image scanning approach in CI.

## Default scanner

- Trivy

## Gate policy

- Prod: fail on HIGH/CRITICAL.
- Dev/test: warn on HIGH/CRITICAL.

## Optional layers

- ECR enhanced scanning (continuous registry scanning).
- Docker Scout (if licensing and org setup allow).

## Implementation notes

- Scan can run before push (local image) or after push (registry image).
- Keep DB updates in CI to avoid stale results.
- Keep thresholds configurable per environment.

## Change process

- Update ADR if policy or tool changes.
- Keep this doc aligned with CI workflows.
