# Build Run Logs

This directory holds per-run records for builds/bootstraps and teardowns.

## Naming convention

- `BR-XXXX-<build-id>.md` for build + bootstrap runs
- `TD-XXXX-<build-id>.md` for teardown runs

`XXXX` is a zero-padded sequence (start at 0001).

## When to add a new entry

- Add a `BR-` entry after a successful build + bootstrap run.
- Add a `TD-` entry after a teardown run (success or failure).

Use `docs/40-delivery/41_BUILD_RUN_LOG.md` as the summary index and link to
these entries for deeper detail.

## Standard Fields

Each log entry should capture:
- **Build ID / Commit:** Traceability to code.
- **Plan Delta:** Number of resources added/changed/destroyed (Blast radius).
- **Duration:** Precise times for Build vs. Bootstrap phases.

