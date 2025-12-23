# Bootstrap Entrypoint

This is the single "entrypoint" directory that answers: how does a blank cluster become a platform?
It captures the intended bootstrap flow and the boundary between cluster creation and platform rollout.

bootstrap/
  README.md
  00_prereqs/
  10_gitops-controller/
  20_core-addons/
  30_platform-tooling/
  40_smoke-tests/

## Recommended sequence

1) 00_prereqs: verify required tools are installed.
2) 10_gitops-controller: install Argo CD via Helm.
3) 20_core-addons: install the AWS Load Balancer Controller and cert-manager.
4) 30_platform-tooling: apply Argo CD apps and install Kong ingress.
5) 40_smoke-tests: validate kubeconfig, metrics, and run the audit report.

Argo CD is where the cluster reconciles against the desired state in this repo.
Once Applications are created, Argo CD keeps them in sync with Git.

## Bootstrap Steps (Full)

Prereqs:

```
bootstrap/00_prereqs/00_check_tools.sh
```

Required inputs (CLI or env vars):

```
TF_VAR_name_prefix=goldenpath-dev-<id>
TF_VAR_build_id=<build-id>
```

Bootstrap sequence:

```
bootstrap/10_gitops-controller/10_argocd_helm.sh <cluster> <region> [values_file]
bootstrap/20_core-addons/10_aws_lb_controller.sh <cluster> <region> <vpc_id> [service_account_name] [service_account_namespace]
bootstrap/20_core-addons/20_cert_manager.sh <cluster> <region> [namespace]
bootstrap/30_platform-tooling/10_argocd_apps.sh dev
bootstrap/30_platform-tooling/20_kong_ingress.sh <cluster> <region> [namespace]
bootstrap/40_smoke-tests/10_kubeconfig.sh <cluster> <region>
bootstrap/40_smoke-tests/20_audit.sh <cluster> <region>
```

Bootstrap runner (recommended):

```
bootstrap-scripts/helm-bootstrap.sh <cluster> <region> [kong-namespace]
```

Post-build sanity checks:

```
kubectl get nodes
kubectl top nodes
kubectl -n argocd get applications
kubectl -n kong get svc
```

Post-bootstrap actions:

- IRSA annotations for cluster-autoscaler and the AWS Load Balancer Controller are created by Terraform service accounts.
- Node access uses SSM by default; enable SSH break-glass only via `enable_ssh_break_glass`.

SSH break-glass example (CLI):

```
terraform -chdir=envs/dev apply -var="enable_ssh_break_glass=true" -var="ssh_key_name=mikeybeezy" -var='ssh_source_security_group_ids=["sg-..."]'
```

CI example (env var):

```
TF_VAR_enable_ssh_break_glass=true TF_VAR_ssh_key_name=mikeybeezy TF_VAR_ssh_source_security_group_ids='["sg-..."]' terraform -chdir=envs/dev apply
```

Note: `ssh_key_name` is the AWS EC2 key pair name (not the local `.pem` file) and is only required when `enable_ssh_break_glass=true`.

Review the dev baseline checklist:

```
bootstrap/40_smoke-tests/30_dev_baseline_checklist.md
```

## Determinism

Bootstrap should be deterministic: with the same Terraform inputs and Git
manifests, the cluster should converge to the same state every time. This is
why Argo CD is the source of truth for apps and versions are pinned where
possible.

## Dev-first standardization

We will standardize dev first: a boilerplate cluster, one stateless app, one
stateful app, and PV/PVC workflows. Once the dev path is stable, we will apply
the same pattern to test/staging/prod.

## Core add-ons (current)

These add-ons are currently installed as EKS managed add-ons during cluster provisioning:

- coredns: cluster DNS for service discovery.
- kube-proxy: Kubernetes service networking on each node.
- vpc-cni: pod networking in the VPC (ENI/IP assignment).
- aws-ebs-csi-driver: block storage for persistent volumes.
- aws-efs-csi-driver: shared file storage for persistent volumes.
- snapshot-controller: CSI volume snapshot APIs.

## Strategy to move add-ons into 20_core-addons/

Short term we use EKS managed add-ons for fast, reliable cluster bring-up.
Longer term, once GitOps is the default, we will shift add-on ownership into
`20_core-addons/` and manage them declaratively (Helm/Kustomize) with version
pinning and configuration overrides. Terraform will keep cluster and node
infrastructure concerns only, while GitOps will manage add-on lifecycle.

## Private subnets and NAT requirement

EKS nodes run in private subnets. They must be able to reach the public AWS
endpoints (EKS API, STS, ECR) to join the cluster. For this, private subnets
need a route to a NAT gateway placed in a public subnet. Without NAT (or VPC
endpoints), node groups will fail to join and add-ons like CoreDNS will stay
degraded.

## First-run note for existing clusters

If a cluster already exists (created outside this Terraform state), import the
existing node group and add-ons before applying, otherwise Terraform will hit
ResourceInUse errors. For a new cluster created by Terraform, no imports are
needed.

Example imports:

```
terraform import 'module.eks[0].aws_eks_node_group.this' <cluster>:<node_group>
terraform import 'module.eks[0].aws_eks_addon.coredns' <cluster>:coredns
terraform import 'module.eks[0].aws_eks_addon.vpc_cni' <cluster>:vpc-cni
terraform import 'module.eks[0].aws_eks_addon.kube_proxy' <cluster>:kube-proxy
terraform import 'module.eks[0].aws_eks_addon.ebs_csi_driver' <cluster>:aws-ebs-csi-driver
terraform import 'module.eks[0].aws_eks_addon.efs_csi_driver' <cluster>:aws-efs-csi-driver
terraform import 'module.eks[0].aws_eks_addon.snapshot_controller' <cluster>:snapshot-controller
terraform import 'module.iam[0].aws_iam_role.eks_cluster' <cluster-role-name>
terraform import 'module.iam[0].aws_iam_role.eks_node_group' <node-role-name>
```

If IAM roles already exist (EntityAlreadyExists), import them instead of recreating.

## Connect to the cluster

To connect with kubectl, update your kubeconfig with the EKS cluster name and region:

```
aws eks update-kubeconfig --region <region> --name <cluster>
kubectl get nodes
```

For validation, use the smoke test script:

```
bootstrap/40_smoke-tests/10_kubeconfig.sh <cluster> <region>
```

This script installs Metrics Server and runs `kubectl top nodes` as a quick
health check.

For a phased audit report after add-ons are installed:

```
bootstrap/40_smoke-tests/20_audit.sh <cluster> <region>
```

Dev baseline checklist:

```
bootstrap/40_smoke-tests/30_dev_baseline_checklist.md
```

## CI note

When CI is introduced, we will run the bootstrap sequence and dev baseline
checks in the pipeline to validate the platform on every change.

## Argo CD access (Keycloak + admin bootstrap)

We will use Keycloak for long-term access. The Argo CD admin password is only for
bootstrap and should be rotated or disabled soon after SSO is working.

How users know it is disabled:
- We will disable admin only via an explicit, manual step (no silent automation).
- The step will log a clear message: "Argo CD admin account disabled" and the
  timestamp will be captured in the audit report.
- After disabling, access is validated via SSO login.

Rollback / recovery:
- Keep the admin account enabled until Keycloak login is verified.
- If access is lost, re-enable admin and rotate the password, then re-apply SSO.
- Keep a break-glass procedure documented (who can re-enable admin, where the
  secret is stored, and how to rotate).

Scripted control (manual and auditable):

```
bootstrap/10_gitops-controller/20_argocd_admin_access.sh disable
bootstrap/10_gitops-controller/20_argocd_admin_access.sh enable
```

## Scripts for each phase

Prereqs:

```
bootstrap/00_prereqs/00_check_tools.sh
```

GitOps controller:

```
bootstrap/10_gitops-controller/10_argocd_helm.sh <cluster> <region> [values_file]
```

Core add-ons (load balancer controller):

```
bootstrap/20_core-addons/10_aws_lb_controller.sh <cluster> <region> <vpc_id> [service_account_name] [service_account_namespace]
bootstrap/20_core-addons/20_cert_manager.sh <cluster> <region> [namespace]
```

Autoscaler (Argo CD):

```
gitops/argocd/apps/dev/cluster-autoscaler.yaml
```

Terraform creates the IRSA service accounts for autoscaler and the AWS Load Balancer Controller.

Autoscaler IRSA annotation is applied via Terraform-managed service accounts, so no manual injection is required.

Platform tooling (apps + ingress):

```
bootstrap/30_platform-tooling/10_argocd_apps.sh <env>
bootstrap/30_platform-tooling/20_kong_ingress.sh <cluster> <region> [namespace]
```

## Kong requirements (Helm/Argo CD)

Kong requires:
- AWS Load Balancer Controller (for ALB/NLB provisioning).
- RBAC and service accounts (provided by the chart/manifest).
- Optional CRDs for Kong plugins and custom resources.
- Optional Postgres (if not running DB-less).

We install Kong through Argo CD so the cluster reconciles with Git state.
Ingress strategy decision (Kong+NLB vs ALB): `docs/08_INGRESS_STRATEGY.md`.
cert-manager is also installed through Argo CD and validated by the script.

## Kong Manager access (temporary)

Kong Manager is enabled for validation but kept private (ClusterIP). For
temporary access, expose it with a Kong Ingress using basic auth, then remove
basic auth once SSO (Keycloak) is in place.

## Keycloak SSO follow-up

For now the priority is: provision the cluster, install ingress/load balancer,
and deploy the core IDP tooling apps. Keycloak SSO integration (including any
prechecks before disabling the Argo CD admin user) is a follow-up task once the
platform baseline is stable.

## Bootstrap components (mandatory vs optional)

Mandatory (baseline cluster functionality):
- metrics-server: resource metrics API for `kubectl top` and autoscaling.
- vpc-cni: pod networking in the VPC (ENI/IP assignment).
- coredns: cluster DNS for service discovery.
- kube-proxy: Kubernetes service networking on each node.
- aws-load-balancer-controller: provisions ALB/NLB for Services/Ingress in AWS.
- cert-manager: automates TLS certificates (e.g., Let's Encrypt).
- kong-ingress-api-gateway: API gateway and ingress controller for north-south traffic.
- cluster-autoscaler: keeps node groups sized for pending workload demand.

Optional (platform capabilities):
- external-dns: automates DNS records (e.g., Route53) for Services/Ingress.
- node-local-dns: per-node DNS cache to reduce CoreDNS load and speed lookups.
- calico: consider in v2 if we need NetworkPolicy enforcement or advanced networking features.
