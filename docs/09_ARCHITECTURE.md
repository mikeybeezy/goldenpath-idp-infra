# Architecture Overview

## Boxed diagram (ASCII)

```

┌───────────────────────────────────────────────┐
│ AWS Account (eu-west-2)                       │
└───────────────────────────────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────────┐
│ VPC 10.0.0.0/16 (goldenpath-dev-vpc)           │
└───────────────────────────────────────────────┘
   │                         │
   │                         │
   ▼                         ▼
┌───────────────────────┐   ┌───────────────────────┐
│ Internet Gateway (igw)│   │ EKS Cluster            │
└───────────────────────┘   │ (goldenpath-dev-eks)   │
   │                        └───────────────────────┘
   │                                  │
   ▼                                  ▼
┌───────────────────────────────────────────────┐
│ Public Subnets                                │
│ - 10.0.1.0/24 (eu-west-2a)                    │
│ - 10.0.2.0/24 (eu-west-2b)                    │
│ Route: 0.0.0.0/0 -> IGW                       │
└───────────────────────────────────────────────┘
   │
   ▼
┌───────────────────────────────────────────────┐
│ NAT Gateway + EIP                              │
└───────────────────────────────────────────────┘
   │
   ▼
┌───────────────────────────────────────────────┐
│ Private Subnets                               │
│ - 10.0.11.0/24 (eu-west-2a)                   │
│ - 10.0.12.0/24 (eu-west-2b)                   │
│ Route: 0.0.0.0/0 -> NAT                       │
└───────────────────────────────────────────────┘
   │
   ▼
┌───────────────────────────────────────────────┐
│ EKS Node Group (managed)                      │
└───────────────────────────────────────────────┘

┌───────────────────────────────────────────────┐
│ IAM (Terraform-managed)                       │
│ - Cluster Role                                │
│ - Node Group Role                             │
│ - IRSA Roles (LB Controller, Autoscaler)      │
└───────────────────────────────────────────────┘

```

## Mermaid diagram (renderable)

```

flowchart TD
  A[AWS Account<br/>eu-west-2] --> VPC[VPC 10.0.0.0/16<br/>goldenpath-dev-vpc]
  VPC --> IGW[Internet Gateway]
  VPC --> EKS[EKS Cluster<br/>goldenpath-dev-eks]
  IGW --> Pub[Public Subnets<br/>10.0.1.0/24 (2a)<br/>10.0.2.0/24 (2b)<br/>Route: 0.0.0.0/0 -> IGW]
  Pub --> NAT[NAT Gateway + EIP]
  NAT --> Priv[Private Subnets<br/>10.0.11.0/24 (2a)<br/>10.0.12.0/24 (2b)<br/>Route: 0.0.0.0/0 -> NAT]
  Priv --> NG[EKS Node Group]
  IAM[IAM (Terraform-managed)<br/>Cluster Role<br/>Node Role<br/>IRSA Roles] --> EKS
  IAM --> NG

```

1.Add BuildId to tags everywhere.
2.Create a cleanup script that finds and deletes tagged orphaned resources.
3.Make name_prefix required and CLI‑driven.

- Create a doc for for Handling falure modes  tthis context is infre build, enter the options surfaced  ptions, the  choice we made and  othre options that could be adopted down the line

- and add to the govnece doc's failure modes look like and how we treat fiald cluster builds

