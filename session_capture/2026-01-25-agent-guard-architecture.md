# Session Capture: AgentGuard Architecture (Use-Case Pivot)

**Date**: 2026-01-25
**Feature**: Universal Agent Context Architecture ("AgentGuard")
**Branch**: `feature/multi-agent-architecture`
**Driver**: Platform Team + Antigravity

## 🎯 Goal
Pivot the repository from an "Internal IDP" to a **"Universal Protocol for Managed AI Agents"** (Target Valuation: £10M+).
Address the risk of "Infinite Context Windows" making simple context management obsolete by shifting value to **Governance/Constitution Enforcment**.

## 🏗️ Architecture: The ".agent/" Standard

We implemented a "Universal BIOS" that forces ANY agent (Claude, Cursor, Copilot) to adhere to the same context rules, via **Redirection** and **Injection**.

### 1. The Kernel (`.agent/`)
*   `README.md`: The "Bootloader" / Router.
*   `context/governance.md`: The immutable "Constitution" (VQ, Gates).
*   `context/session-current.md`: The "Shared Memory Bridge" for multi-agent collaboration.

### 2. The Trap (Universal Redirection)
We hijacked the default configuration files to point to our Kernel:
*   `CLAUDE.md` -> Reads `.agent/README.md`
*   `.cursorrules` -> Reads `.agent/README.md`
*   `.github/copilot-instructions.md` -> Reads `.agent/README.md`

### 3. The Safety Net (Header Injection)
Created `scripts/inject_agent_headers.py`.
*   **Function**: Stamps critical files (.py, .tf, .md) with `<!-- AGENT_CONTEXT: Read .agent/README.md -->`.
*   **Result**: Even "dumb" agents or random file opens trigger a "Context Alert" in the LLM's window.

## 💰 Valuation Thesis (£10M+)
*   **Problem**: Enterprise Fear of Ungoverned AI.
*   **Solution**: Protocol-based enforcement of "Corporate Law" (Governance) into the AI's context.
*   **Moat**: The "Open Standard" (`.agent/`) + The "Closed Binary" (`agent-guard` CI check, to be built).

## ✅ Verification
*   Ran `scripts/inject_agent_headers.py`: 270+ files updated.
*   Verified redirection files exist in root.
*   Pushed to `feature/multi-agent-architecture`.

## ⏭️ Next Actions
*   [ ] Merge to `development`.
*   [ ] Build the "Agent Guard" CI Binary (Open Core strategy).
*   [ ] Market the `.agent/` standard to other teams.
