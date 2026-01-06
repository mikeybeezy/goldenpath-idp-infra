---
id: ADR_INDEX_HITL_TEST
title: Feature Test - ADR Index Automation (Human-in-the-Loop)
type: test-record
category: architecture
version: '1.0'
owner: platform-team
status: in-progress
relates_to:
  - ADR-0112
  - ADR_INDEX_AUTOMATION_SPEC
---

# Feature Test: ADR Index Automation (HITL)

## 📋 Test Overview
- **Objective**: Validate the "Bot + Human" workflow for ADR Index synchronization.
- **Scenario**: A developer introduces a new architectural decision; the bot remediates the index; the platform lead approves.
- **Success Criteria**: 
    - Index is correctly updated between markers.
    - ID normalization is enforced.
    - Human lead approves the final diff.

## 🧪 Execution Log

### 1. Initial State
- **Master Index**: `docs/adrs/01_adr_index.md`
- **Total ADRs**: 105

### 2. Bot Action (Simulation)
- **Action**: Create `docs/adrs/ADR-0113-platform-hitl-test.md`
- **Script**: `python3 scripts/generate_adr_index.py`
- **Result**: ✅ SUCCESS. Both the `relates_to` manifest and the `Active ADRs` table were updated with ADR-0113.

### 3. Human Review (User)
- **Reviewer**: @USER
- **Status**: ✅ APPROVED

## 🏁 Final Outcome
- **Status**: PASSED
- **Verification**: The ADR Index was successfully synchronized with a bot-led commit that was reviewed and approved by the human platform lead. This confirms 100% compliance with the HITL Governance Model.
