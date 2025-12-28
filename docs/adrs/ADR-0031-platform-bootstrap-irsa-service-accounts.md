# ADR-0031: Create IRSA service accounts during bootstrap

- **Status:** Accepted
- **Date:** 2025-12-28
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Operations | Delivery
- **Related:** bootstrap/10_bootstrap/README.md, docs/21_CI_ENVIRONMENT_CONTRACT.md

---

## Context

The AWS Load Balancer Controller and Cluster Autoscaler require IRSA-backed
service accounts to exist before the controllers are installed. Early runs failed
when the controllers were installed first, leading to non-deterministic bootstrap
errors and partial installs.

We need a reliable ordering that avoids race conditions and keeps bootstrap
deterministic in V1.

## Decision

We will create the IRSA service accounts as a **bootstrap stage** (Stage 3B),
using a targeted Terraform apply when `ENABLE_TF_K8S_RESOURCES=true`.

If `ENABLE_TF_K8S_RESOURCES=false`, bootstrap will **require** those service
accounts to already exist and will fail fast if they are missing.

## Scope

Applies to:
- `kube-system/aws-load-balancer-controller`
- `kube-system/cluster-autoscaler`

Does not apply to:
- Other Kubernetes resources
- Non-IRSA service accounts

## Consequences

### Positive

- Deterministic ordering and fewer bootstrap failures.
- Clear responsibility for IRSA preconditions.
- Fast feedback when service accounts are missing.

### Tradeoffs / Risks

- Adds a Terraform apply step during bootstrap.
- Requires kubeconfig access earlier in the flow.

### Operational impact

- Operators must keep `ENABLE_TF_K8S_RESOURCES` aligned with actual SA ownership.
- If SAs are managed outside Terraform, they must exist before bootstrap.

## Alternatives considered

- **Install controllers first and retry on failure:** rejected due to flakiness.
- **Create service accounts outside bootstrap:** rejected because it removed the
  explicit ordering and caused silent failures.

## Follow-ups

- Revisit once the end-to-end CI flow is stable.
- Evaluate whether IRSA SAs should move back into core Terraform apply.

## Notes

Accepted for V1 with openness to alternatives once CI is fully stable.
