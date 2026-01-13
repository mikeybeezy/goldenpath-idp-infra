---
id: ADR-0152-vpc-endpoints-for-private-clusters
title: 'ADR-0152: Implementation of VPC Endpoints for Private Cluster Connectivity'
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

# ADR-0152: Implementation of VPC Endpoints for Private Cluster Connectivity

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
# Decision Matrix: NAT Gateway vs. VPC Endpoints for EKS Private Connectivity

## Overview
This document analyzes the trade-offs between using **NAT Gateways** versus **VPC Interface Endpoints (PrivateLink)** for enabling connectivity for private EKS worker nodes.

The primary use case is allowing nodes in private subnets to reach AWS services required for bootstrapping:
1.  **ECR** (Container Registry) - `ecr.api`, `ecr.dkr`
2.  **S3** (Layers/State) - `s3`
3.  **EC2** (Node Metadata/ENIs) - `ec2`
4.  **STS** (IAM Roles) - `sts`

## 1. Comparison Matrix

| Feature | **NAT Gateway** strategy | **VPC Endpoints** strategy |
| :--- | :--- | :--- |
| **Connectivity Model** | Outbound via Internet (Egress `0.0.0.0/0` -> NAT -> IGW) | Internal AWS Backbone (Direct Private Link) |
| **Reliability** | **Medium**. Depends on public DNS resolution, IGW availability, and route propagation. Subject to internet routing issues. | **High**. Traffic never leaves the AWS network. Immune to internet outages or DNS spoofing. |
| **Security** | **Medium/Low**. Traffic traverses public IP space (though encrypted). Requires granting outbound internet access to nodes. | **High**. Nodes can be completely air-gapped (no internet access). Can use Endpoint Policies to restrict access to specific buckets/registries. |
| **Scalability** | **High**. A single NAT GW per AZ handles all outbound traffic for all subnets. Throughput scales automatically (up to 100Gbps). | **High**. Endpoints scale automatically (up to 100Gbps). However, limits exist on number of endpoints per VPC (configurable). |
| **Complexity** | **Low**. Single resource (`aws_nat_gateway`) covers all use cases (AWS services + 3rd party APIs). | **Medium**. Requires managing separate resources for each AWS service (`ecr`, `s3`, `ec2`, `sts`, `logs`, etc.). |
| **Cost Structure** | **Hourly + Data**. ~$0.045/hr + $0.045/GB processed. | **Hourly + Data**. ~$0.01/hr per ENI per AZ + $0.01/GB processed. (See detailed breakdown below). |

## 2. Cost Analysis (Monthly Estimates)

Assuming `eu-west-2` (London) pricing, 2 Availability Zones (AZs), and 500GB of traffic (mostly image pulls).

### Scenario A: NAT Gateway
*   **Hourly**: 2 NAT GWs * $0.045/hr * 730 hrs = **$65.70**
*   **Data Processing**: 500GB * $0.045/GB = **$22.50**
*   **Total Monthly**: **~$88.20**

### Scenario B: VPC Endpoints (4 Services: ECRx2, EC2, STS + S3 Gateway)
*   **Hourly**: 4 Interface Endpoints * 2 AZs * $0.01/hr * 730 hrs = **$58.40**
    *   *Note: S3 Gateway Endpoint is FREE.*
*   **Data Processing**: 500GB * $0.01/GB = **$5.00**
*   **Total Monthly**: **~$63.40**

**Winner**: VPC Endpoints are surprisingly **cheaper** if you have meaningful data volume, because the per-GB processing fee ($0.01 vs $0.045) is significantly lower.

## 3. Complexity & Operational Overhead

### NAT Gateway
*   **Pros**: "Set and Forget". If a node needs to talk to *any* new service (e.g., `github.com`, `pypi.org`), it just works.
*   **Cons**: Single point of failure for internet access. Harder to audit specific traffic flows.

### VPC Endpoints
*   **Pros**: Granular control.
*   **Cons**: Whitelist approach. If you install a tool that needs to talk to `docker.io` (instead of ECR) or `pypi.org` (for Python packages), it will **FAIL** unless you *also* have a NAT Gateway or a Proxy.
    *   *Mitigation*: Most "Golden Path" platforms run a Hybrid model: VPC Endpoints for high-volume internal traffic (ECR/S3) + NAT for low-volume external traffic.

## 4. Recommendation for Golden Path

**Hybrid Approach**:
1.  Use **VPC Endpoints** for `ECR`, `S3`, `EC2`, `STS`.
    *   **Reason**: Critical boot path reliability, lower cost for heavy image pulls, better security.
2.  Retain **NAT Gateway** (small scale).
    *   **Reason**: Developers will inevitably need to pull a helm chart from the internet or a library from NPM/PyPI. Without NAT, the platform becomes too restrictive for general development.

## 5. Decision
Enable the full suite of VPC Endpoints (`ec2`, `sts`, `ecr.api`, `ecr.dkr`, `s3`) immediately to resolve the `NodeCreationFailure`.
