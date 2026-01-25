<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: ADR-0154
title: Promote Bootstrap V3 as Default
type: adr
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0148-seamless-build-deployment-with-immutability
  - ADR-0153
  - ADR-0154
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-14
deciders:
  - Platform Team
consents:
  - Architecture Review Board
---

## Promote Bootstrap V3 as Default

## Context

The platform bootstrap logic (`bootstrap/`) has evolved through versions `v1` (legacy), `v2` (interim), and `v3` (current).
The default `Makefile` configuration pointed to `v1`. However, during the implementation of Seamless Build Deployments (ADR-0148), we identified that `v1` lacks critical resilience features found in `v3`:

1. **Context Awareness**: `v3` correctly handles unique, timestamped Cluster Names passed from the Makefile (`goldenpath-dev-eks-XX-XX-XX-YY`), whereas `v1` often assumed a static cluster name.
2. **Robust Preflight**: `v3` includes stronger preflight checks for node capacity and tool versions.
3. **Governance Compatibility**: `v3` has been patched (along with shared scripts) to handle governance metadata files (`metadata.yaml`) correctly during ArgoCD app application, preventing deployment failures.

## Decision

We promote **Bootstrap V3** (`bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh`) to be the **Default** bootstrap version in the root `Makefile`.

Additionally, we implement **Dynamic Cluster Discovery** in the `Makefile`.Instead of relying on rigid string concatenation to guess the cluster name, the Makefile now queries the AWS Resource Groups Tagging API to find the cluster ARN associated with the current `BUILD_ID`.

```makefile
CLUSTER_ARN := $(shell aws resourcegroupstaggingapi get-resources ... filters Key=BuildId,Values=$(BUILD_ID) ...)
```

This decouples the orchestration logic (Makefile) from the implementation details (Terraform naming conventions), ensuring that subsequent bootstrap phases always target the correct, actual infrastructure.

All future invocations of `make deploy` or `make bootstrap` will use `v3` unless explicitly overridden.

## Consequences

### Positive

* **Consistency**: New deployments automatically benefit from the latest resilience fixes.
* **Resilience**: Reduced likelihood of "Cluster Not Found" or "Manifest Apply" errors.
* **Alignment**: Matches the `make deploy` workflow developed for ephemeral builds.

### Negative

* **Legacy impact**: If any workflows specifically relied on `v1` idiosyncrasies without pinning the version, they may behave differently (though `v3` is designed to be backward compatible in usage).
