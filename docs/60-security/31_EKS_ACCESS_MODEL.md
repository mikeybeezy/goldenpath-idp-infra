---
id: 31_EKS_ACCESS_MODEL
title: EKS Access Model (Living)
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - 33_IAM_ROLES_AND_POLICIES
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: security
status: active
version: '1.0'
dependencies: []
supported_until: 2028-01-01
breaking_change: false
---

# EKS Access Model (Living)

This document captures the current EKS access model, how it is operated in V1,
and the commands used to manage and verify access. It evolves as the platform
matures.

---

## Quick reference

### Get your IAM user ARN

```sh
aws sts get-caller-identity --query "Arn" --output text
```

---

## Model overview

```text
                           AWS ACCOUNT
+------------------------------+
|                                                            |
|  [GitHub Actions OIDC]  --->  AssumeRole (CI Bootstrap)     |
|                                        |                    |
|                                        v                    |
|                                 EKS Cluster Admin           |
|                                                            |
|  [Humans] ----------->  Access Entry + Policy         |
|                                      (EKS API)              |
|                                                            |
|  [Workloads] -> ServiceAccount -> IRSA Role -> AWS APIs     |
|                                                            |
+------------------------------+
```

---

## Commands (placeholders)

Placeholders are indicated with angle brackets (e.g., `<CLUSTER_NAME>`).

### Create access entry

```sh
aws eks create-access-entry \
  --cluster-name <CLUSTER_NAME> \
  --principal-arn "<IAM_USER_OR_ROLE_ARN>" \
  --region <AWS_REGION>
```

### Associate access policy

```sh
aws eks associate-access-policy \
  --cluster-name <CLUSTER_NAME> \
  --principal-arn "<IAM_USER_OR_ROLE_ARN>" \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/<POLICY_NAME> \
  --access-scope type=cluster \
  --region <AWS_REGION>
```

---

## Basic cluster checks (AWS CLI)

### List clusters (table)

```sh
aws eks list-clusters --region <AWS_REGION> --output table
```

### Get cluster status

```sh
aws eks describe-cluster \
  --name <CLUSTER_NAME> \
  --region <AWS_REGION> \
  --query "cluster.status" \
  --output text
```

### Get cluster details

```sh
aws eks describe-cluster \
  --name <CLUSTER_NAME> \
  --region <AWS_REGION> \
  --query "cluster"
```

## Notes

- Bootstrap access is granted to the IAM principal that creates the cluster.
- Human access is explicit via access entries and policies.
- Workload access uses IRSA and is separate from human access.

## Terraform Authentication

Terraform manages Kubernetes resources (via the `kubernetes` and `helm` providers) by authenticating as the IAM Role running the apply. We avoid static tokens. Instead, we use the `exec` plugin to generate short-lived tokens on demand:

```hcl
provider "kubernetes" {
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    args        = ["eks", "get-token", "--cluster-name", var.cluster_name]
    command     = "aws"
  }
}
```

 This ensures that:

 1. **Zero Trust**: No long-lived secrets are stored in the state.
 2. **Robustness**: Authentication refreshes automatically if the apply takes longer than 15 minutes.
 3. **Traceability**: All API actions are logged in CloudTrail as the assumed IAM Role.

## Related docs

- `docs/60-security/33_IAM_ROLES_AND_POLICIES.md`
