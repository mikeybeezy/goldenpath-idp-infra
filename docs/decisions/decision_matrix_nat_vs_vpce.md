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
