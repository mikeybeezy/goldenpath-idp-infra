<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
# Protocol: HOTFIX

**Intent**: Critical fix for production/main.

## Steps
1.  **Check Prerequisites**:
    *   Are you on `main` branch?
    *   Is `bin/governance pulse` showing alerts?
2.  **Create Branch**: `hotfix/description-of-fix`
3.  **Code**:
    *   Minimal changes only.
    *   No refactoring.
4.  **Verify**:
    *   Run `pytest` related to change.
5.  **Commit**:
    *   Msg: `fix: <description> [HOTFIX]`
6.  **PR**:
    *   Label: `hotfix`
    *   VQ Class: `HV/HQ` (High Value / High Quality)
    *   Description: "URGENT FIX: <reason>"
