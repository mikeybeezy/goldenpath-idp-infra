<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
# Protocol: FEATURE

**Intent**: New capability or improvement.

## Steps
1.  **Check Prerequisites**:
    *   Are you on `development` branch?
2.  **Create Branch**: `feature/description`
3.  **Code**:
    *   Follow `docs/00-foundations/00_DESIGN_PHILOSOPHY.md`.
    *   If adding new infra, update `envs/dev/`.
    *   If adding docs, use `scripts/scaffold_doc.py`.
4.  **Verify**:
    *   Run `bin/governance test`.
5.  **Commit**:
    *   Msg: `feat: <description>`
6.  **PR**:
    *   Target: `development`
    *   VQ Class: `MV/HQ` or `LV/LQ` depending on maturity.
