---
id: ADR-0113
title: 'ADR-0113: Platform HITL Testing Protocol'
type: adr
category: governance
version: '1.0'
owner: platform-team
status: proposed
date: 2026-01-06
relates_to:
  - ADR-0112
---

# ADR-0113: Platform HITL Testing Protocol

## Context
As we move toward a more automated documentation governance model, we need a standard protocol for "Human-in-the-Loop" (HITL) verification of bot-generated changes. This ensures that while the speed of documentation increases, the accuracy and human authority remain supreme.

## Decision
We will use formal feature test records at `tests/feature-tests/` to capture the outcome of HITL simulations.
