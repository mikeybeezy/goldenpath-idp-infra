---
id: EC-0005-k8s-extensibility-strategy
title: Harnessing the K8s API (Controllers & Reconciliation)
type: capability-extension
status: proposed
relates_to:
  - EC-0001
  - EC-0002
tags:
  - kubernetes
  - operators
  - crossplane
  - kyverno
  - architecture
---

# Harnessing the K8s API: Moving Beyond Scripts

## Context
The current platform relies heavily on "One-Off Triggers" (GitHub Actions -> Python Scripts) for automation. To scale, we must move towards **"Continuous Reconciliation"** (Operator -> Desired State Loop) inherent to the Kubernetes API.

## Extensibility Strategy: The 3 Levels

### 1. Compliance Controllers (Policy-as-Code)
*   **The Problem**: Validation logic is scattered in CI pipelines or Python scripts.
*   **The K8s Solution**: **Kyverno** (Cluster Admission Controller).
*   **Mechanism**: Define `ClusterPolicy` CRDs. The API server validates requests before they persist.
*   **Example**: "All `SecretRequests` must have a `risk` label."
*   **Benefit**: Rejects bad data at the gate. Cleaner than imperative `if/else` logic.
*   **Action**: Adopt Kyverno policies to replace custom Python validation logic.

### 2. Infrastructure Controllers (Composite Resources)
*   **The Problem**: Imperative provisioning scripts (`rds_provision.py`) are brittle. If they crash, resources are left in inconsistent states.
*   **The K8s Solution**: **Crossplane**.
*   **Mechanism**:
    1.  Define a `CompositeResourceDefinition` (XRD) (e.g., `GoldenPathDatabase`).
    2.  Create a `Composition` mapping the XRD to real resources (AWS RDS Instance + K8s Secret + Helm Release).
    3.  **Reconciliation**: The controller continuously watches the resource. If changed/deleted externally, it is immediately self-healed.
*   **Benefit**: Declarative Infrastructure-as-Data. No more "Create vs Delete" scripts.
*   **Action**: Prioritize replacing `rds_provision.py` with a Crossplane Composition.

### 3. Custom Controllers (The "Operator Pattern")
*   **The Problem**: Complex "Glue" logic (e.g., `goldenpath-idp-teardown-v3.sh`) exists to clean up hanging dependencies like ALBs.
*   **The K8s Solution**: **Finalizer Operator**.
*   **Mechanism**: A custom controller (Kubebuilder/Kopf) watches resources. On deletion, it executes cleanup logic *before* removing the finalizer and allowing deletion.
*   **Benefit**: Elimination of massive Bash cleanup scripts. Lifecycle logic lives inside the cluster.

---

## Verdict & Recommendation

**Recommendation for V1:**
Avoid writing custom operators (Level 3) initially as they incur high maintenance.

**Strategic Pivot:**
1.  **Skip Level 3 (Custom Operators)** for now.
2.  **Adopt Level 2 (Crossplane)** immediately. It standardizes the "Golden Path" definition into Kubernetes CRDs, effectively replacing the current imperative Python/Terraform wrapping.

---
**Signed:** Antigravity Agent
**Timestamp:** 2026-01-17T23:00:19Z
