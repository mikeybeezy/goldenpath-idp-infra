# Rebuild Sequence (Stub)

## Intent
Define the minimum, repeatable sequence to rebuild platform infrastructure and
restore core services after a teardown or failure.

## Scope (planned)
- Prerequisites and safety checks.
- Ordered steps (infra -> bootstrap -> GitOps sync -> validation).
- Required inputs (env, build_id, lifecycle).
- Signals/criteria that declare each phase "ready."

## Notes
- This file is a stub to anchor ADR references until the full runbook is written.
- Related: `docs/70-operations/15_TEARDOWN_AND_CLEANUP.md`.
