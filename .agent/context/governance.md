<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
# Governance & Rules (The Constitution)

## 1. Value Quantification (VQ)
**Rule**: Every PR must have `VQ Class` and `Impact Tier`.
*   `HV/HQ` (High Value/High Quality): Core infrastructure. Risk averse.
*   `LV/LQ` (Low Value/Low Quality): Prototypes/Scripts. Speed first.
*   **Ref**: `docs/00-foundations/product/VQ_TAGGING_GUIDE.md`

## 2. PR Guardrails
**Rule**: You must verify against `scripts/pr_guardrails.py`.
*   **Agents**: You are explicitly checked for `VQ Class`.
*   **Docs**: If only `.md` files change, label `docs-only`.
*   **Hotfix**: Must target `main` and be from `platform-team`.

## 3. Emoji Policy
**Rule**: Use emojis in commit messages and PR titles for visual grep.
*   ✨ `feat`
*   🐛 `fix`
*   📚 `docs`
*   ♻️ `refactor`
*   🛡️ `security`

## 4. Tests
**Rule**: Run `bin/governance test` before commit.
