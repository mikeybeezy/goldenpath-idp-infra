---
id: 01_EKS_ACCESS_RECOVERY
title: EKS Access Recovery (Runbook)
type: runbook
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: medium
  security_risk: access
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
- 31_EKS_ACCESS_MODEL
---

# EKS Access Recovery (Runbook)

This runbook provides the step-by-step procedure to restore access to an EKS
cluster and refresh your kubeconfig.

Use this when:

- A new cluster was created and you need initial access.
- Your access entry/policy was not created by Terraform or bootstrap.
- Your local kubeconfig is missing or stale.
- You can reach AWS but kubectl says you are not authorized.

## Prerequisites

- You are authenticated to AWS in the correct account.
- You know the cluster name and region.
- You have your IAM user or role ARN.

## Step 1: Confirm the cluster exists

Why: Ensures you are targeting a real cluster in the correct region.

```sh
aws eks list-clusters --region <AWS_REGION> --output table
```

## Step 2: Create an access entry for your IAM principal

Why: Registers your IAM user or role with the EKS access system.

```sh
aws eks create-access-entry \
  --cluster-name <CLUSTER_NAME> \
  --principal-arn "<IAM_USER_OR_ROLE_ARN>" \
  --region <AWS_REGION>
```

Note: If you see `ResourceInUseException`, the access entry already exists.

## Step 3: Associate an access policy

Why: Grants permissions (for example, admin access) within the cluster.

```sh
aws eks associate-access-policy \
  --cluster-name <CLUSTER_NAME> \
  --principal-arn "<IAM_USER_OR_ROLE_ARN>" \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy \
  --access-scope type=cluster \
  --region <AWS_REGION>
```

## Step 4: Update kubeconfig and verify access

Why: Updates your local kubeconfig to point to the cluster and validates access.

```sh
aws eks update-kubeconfig --name <CLUSTER_NAME> --region <AWS_REGION>
kubectl get ns
```

## Step 5: Inspect workloads (optional)

Why: Confirms you can read cluster-wide resources.

```sh
kubectl get pods -A
```

## Related docs

- `docs/60-security/31_EKS_ACCESS_MODEL.md`
