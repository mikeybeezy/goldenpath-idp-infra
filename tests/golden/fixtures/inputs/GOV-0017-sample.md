---
id: GOV-0017-tdd-and-determinism
title: TDD and Determinism Policy
type: governance
owner: platform-team
status: active
domain: platform-core
lifecycle: active
schema_version: 1
relates_to:
  - ADR-0182-tdd-philosophy
  - GOV-0016-testing-stack-matrix
supported_until: '2028-01-01'
effective_date: 2026-01-26
---

# GOV-0017: TDD and Determinism Policy

## Purpose

This policy defines the testing and determinism requirements for all code changes in the GoldenPath IDP.

## Core Principle

> "Nothing that generates infrastructure, parses config, or emits scaffolds may change without tests."

Tests are not documentation. Tests are **executable contracts** that:
1. Define expected behavior before implementation
2. Catch regressions immediately
3. Enable safe refactoring
4. Preserve determinism across agent and human contributors

## Scope of Determinism

The following components are **determinism-critical** and require test coverage:

| Component | Examples | Why Critical |
|-----------|----------|--------------|
| **Parsers** | YAML frontmatter, config loaders | Incorrect parsing corrupts downstream state |
| **Generators** | Doc scaffolds, template renderers | Output drift breaks consumers |
| **Metadata Engines** | standardize_metadata.py | Metadata is the source of truth |

## Coverage Targets

| Layer | V1 Target | V1.1 Target |
|-------|-----------|-------------|
| Python scripts | 60% | 80% |
| Shell scripts | 40% | 60% |

## References

- ADR-0182: TDD Philosophy
- GOV-0016: Testing Stack Matrix
