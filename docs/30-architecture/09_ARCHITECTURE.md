---
id: 09_ARCHITECTURE
title: Architecture Overview
type: documentation
category: 30-architecture
version: 1.0
owner: platform-team
status: active
dependencies:
- module:vpc
- module:aws_eks
- module:aws_iam
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
- 14_MODULES_OVERVIEW
- 07_REPO_DECOUPLING_OPTIONS
---

# Architecture Overview

## Boxed diagram (ASCII)

```text

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

```mermaid
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
