---
id: ADR-0149-vpc-endpoints-for-private-clusters
title: 'ADR-0149: Implementation of VPC Endpoints for Private Cluster Connectivity'
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to: []
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: '2028-01-01'
---

# ADR-0149: Implementation of VPC Endpoints for Private Cluster Connectivity

## Proposer
Platform Team

## Status
Proposed

## Context
The "Born Governed" EKS platform mandates that worker nodes reside in private subnets to minimize attack surface. However, nodes in private subnets require connectivity to AWS services (specifically ECR for container images and S3 for layers/state) to bootstrap successfully.

Attempts to rely solely on NAT Gateways for this traffic have proven flaky during node initialization, leading to `NodeCreationFailure` and timeouts. Additionally, relying on NAT for internal AWS traffic incurs higher latency and data processing costs, while exposing traffic to the public internet egress path.

## Decision
We will implement **AWS VPC Endpoints (PrivateLink)** for critical services required for EKS bootstrapping.

Specifically, we will add:
1.  **ECR API Endpoint** (`com.amazonaws.region.ecr.api`): For Docker login and image manifest retrieval.
2.  **ECR DKR Endpoint** (`com.amazonaws.region.ecr.dkr`): For pulling the actual container image layers.
3.  **S3 Gateway Endpoint** (`com.amazonaws.region.s3`): Required by ECR (which stores layers in S3) and generally useful for private subnet access to S3 without NAT.

## Consequences
### Positive
*   **Reliability**: Removes dependency on NAT/IGW for cluster bootstrapping. Nodes can join even if upstream internet connectivity is degraded.
*   **Security**: Traffic to ECR and S3 remains entirely on the AWS Backbone Network, satisfying strict "Data Sovereignty" and "Private Networking" requirements.
*   **Performance**: Lower latency for image pulls.

### Negative
*   **Cost**: VPC Interface Endpoints incur a fixed hourly cost (~$7.20/month per endpoint per AZ) plus data processing fees. This increases the base cost of the VPC by approximately $20-30/month.
*   **Complexity**: Adds Terraform resources (`aws_vpc_endpoint`) to the networking module.

## Governance
This architectural change aligns with the "Born Governed" framework by prioritizing security (private networking) and reliability over raw cost optimization.
