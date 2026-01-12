---
id: APPS_HOW_IT_WORKS
title: How It Works Index
type: documentation
---

# How It Works

This directory contains high-level, technical explanations of the platform's core mechanics. It focuses on the "Intent-based" model of the Golden Path, explaining the relationship between developer manifests and final infrastructure.

## Explanations
1. [Secret Request Flow](SECRET_REQUEST_FLOW.md): How application secrets are governed and projected from Git to Kubernetes.
2. [ECR Request Flow](ECR_REQUEST_FLOW.md): The self-service lifecycle of container registry provisioning.
3. [PR Guardrails](PR_GUARDRAILS.md): How the platform enforces quality and governance on code changes.
4. [Documentation Auto-Healing](DOC_AUTO_HEALING.md): Keeping indices and dashboards synchronized with repository reality.
5. [Script Traceability](PR_GUARDRAILS.md#script-traceability): Ensuring every automation script is linked to a design decision (ADR) and a historical record (CL).

## Platform Capabilities
- **Deterministic Scripting**: All platform automation is "Born Governed" with schema-validated headers.
- **Continuous Traceability**: Machine-enforced linking between code, decisions, and history.
- **Automated Remediation**: Self-healing documentation and configuration through governance "healers".
- **Registry Mirroring**: Decoupled observation of platform health to prevent commit contention.
