---
id: ADR-0070-platform-terraform-aws-lb-controller
title: 'ADR-0070: Terraform Management of AWS Load Balancer Controller'
type: adr
status: active
domain: platform-core
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle: active
version: '1.0'
relates_to:
  - ADR-0063
  - ADR-0063-platform-terraform-helm-bootstrap
  - ADR-0070
supported_until: 2028-01-04
breaking_change: false
---

# ADR-0070: Terraform Management of AWS Load Balancer Controller

- **Status:** Proposed
- **Date:** 2026-01-02
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Architecture
- **Related:** `docs/adrs/ADR-0063-platform-terraform-helm-bootstrap.md`

---

## Context

The AWS Load Balancer Controller is a critical component that bridges Kubernetes Ingress objects to AWS Application Load Balancers (ALBs). Without it, Ingress resources (like Kong) remain in a pending state.

Currently, this component is installed via an imperative Bash script (`bootstrap/30_core-addons/10_aws_lb_controller.sh`) which manually runs `helm upgrade --install`. This is done to inject dynamic infrastructure values (VPC ID, Cluster Name) that are difficult to manage in pure static GitOps.

However, this imperative step breaks the "single click" deployment model established in [ADR-0063](./ADR-0063-platform-terraform-helm-bootstrap.md). Unless the operator remembers to run the script, the platform will be broken.

---

## Decision

We will **move the installation of the AWS Load Balancer Controller into Terraform** as a `helm_release` resource within the `kubernetes_addons` module.

1. **Declarative Definition**: The controller will be defined in HCL, with `vpcId`, `clusterName`, and `region` passed as variables from the `aws_eks` and `vpc` modules.
2. **Explicit Dependency**: We will use Terraform `depends_on` to ensure the controller is fully installed before bootstrapping any applications that require a LoadBalancer (e.g., Kong).
3. **Removal of Scripts**: The legacy `10_aws_lb_controller.sh` script will be deleted.

---

## Consequences

### Positive

- **Reliability**: The controller is guaranteed to be present if `terraform apply` succeeds.
- **Configuration Accuracy**: VPC IDs and Region are passed directly from the source of truth (Terraform state) rather than relying on script arguments or environment variables.
- **Architecture Preserved**: This does not change the runtime architecture (Kong -> Ingress -> AWS LB Controller -> ALB). It only changes the *installation method*.

### Tradeoffs

- **State Migration**: Existing clusters managed via script will need their Helm release imported into Terraform state or simply overwritten (Helm handles this gracefully).
