# EKS Access Model (Living)

This document captures the current EKS access model, how it is operated in V1,
and the commands used to manage and verify access. It evolves as the platform
matures.

---

## Model overview

```text
                           AWS ACCOUNT
+------------------------------------------------------------+
|                                                            |
|  [GitHub Actions OIDC]  --->  AssumeRole (CI Bootstrap)     |
|                                        |                    |
|                                        v                    |
|                                 EKS Cluster Admin           |
|                                                            |
|  [Humans] ----------------->  Access Entry + Policy         |
|                                      (EKS API)              |
|                                                            |
|  [Workloads] -> ServiceAccount -> IRSA Role -> AWS APIs     |
|                                                            |
+------------------------------------------------------------+
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

---

## Notes

- Bootstrap access is granted to the IAM principal that creates the cluster.
- Human access is explicit via access entries and policies.
- Workload access uses IRSA and is separate from human access.

## Related docs

- `docs/33_IAM_ROLES_AND_POLICIES.md`
