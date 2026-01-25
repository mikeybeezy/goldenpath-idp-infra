<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
# Deployment & Safety

## The Golden Path
1.  **Local**: `bin/governance setup` -> `bin/governance test`
2.  **Pull Request**: Open against `development`.
    *   CI Gates: Metadata check, Lint, Test.
    *   Guardrails: `pr_guardrails.py` must pass.
3.  **Merge**: Auto-deploy to `dev` cluster via ArgoCD.
4.  **Promote**: `bin/promote --to=staging` (Manual gate).

## Critical Safety Rules
*   **NEVER** edit Terraform state manually.
*   **NEVER** apply to `prod` from local machine (CI only).
*   **ALWAYS** verify `terraform plan` output in PR comments.
*   **ALWAYS** check `bin/governance pulse` before starting big work.

## Teardown
If working in ephemeral environment:
*   Run `bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v5.sh`
*   Verify 0 orphans.
