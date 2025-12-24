# Bootstrap Entrypoint

This directory is the single entrypoint that answers: how does a blank cluster
become a platform? It captures the intended bootstrap flow and the boundary
between cluster creation and platform rollout.

bootstrap/0.5_BOOTSTRAP/
  README.md
  00_prereqs/
  10_gitops-controller/
  20_core-addons/
  30_platform-tooling/
  40_smoke-tests/
  helm-bootstrap.sh
  cleanup-orphans.sh
  pre-destroy-cleanup.sh
  drain-nodegroup.sh
  11_ONE_STAGE_VS_MULTISTAGE_BOOTSTRAP.md

## Recommended sequence

1) 00_prereqs: verify required tools are installed and run EKS preflight.
2) 10_gitops-controller: install Argo CD via Helm.
3) 20_core-addons: validate AWS LB Controller and cert-manager.
4) 30_platform-tooling: apply Argo CD apps and validate Kong ingress.
5) 40_smoke-tests: validate kubeconfig, metrics, and run the audit report.

Argo CD is where the cluster reconciles against the desired state in this repo.
Once Applications are created, Argo CD keeps them in sync with Git.

## One-stage vs multi-stage

Guidance and use cases are in:
`bootstrap/0.5_BOOTSTRAP/11_ONE_STAGE_VS_MULTISTAGE_BOOTSTRAP.md`

## Prereqs (mandatory)

```
bootstrap/0.5_BOOTSTRAP/00_prereqs/00_check_tools.sh
bootstrap/0.5_BOOTSTRAP/00_prereqs/10_eks_preflight.sh <cluster> <region> <vpc-id> <private-subnet-ids> <node-role-arn> <instance-type>
```

## Bootstrap runner (recommended)

```
NODE_INSTANCE_TYPE=t3.small bash bootstrap/0.5_BOOTSTRAP/helm-bootstrap.sh <cluster> <region> [kong-namespace]
```

Optional scale-down after bootstrap:

```
NODE_INSTANCE_TYPE=t3.small SCALE_DOWN_AFTER_BOOTSTRAP=true TF_DIR=goldenpath-idp-infra/envs/dev \
  bash bootstrap/0.5_BOOTSTRAP/helm-bootstrap.sh <cluster> <region>
```

## Full manual sequence (multi-stage)

```
bash bootstrap/0.5_BOOTSTRAP/00_prereqs/00_check_tools.sh
bash bootstrap/0.5_BOOTSTRAP/00_prereqs/10_eks_preflight.sh <cluster> <region> <vpc-id> <private-subnet-ids> <node-role-arn> <instance-type>

bash bootstrap/0.5_BOOTSTRAP/10_gitops-controller/10_argocd_helm.sh <cluster> <region> [values_file]

bash bootstrap/0.5_BOOTSTRAP/20_core-addons/10_aws_lb_controller.sh <cluster> <region> <vpc_id> [service_account_name] [service_account_namespace]
bash bootstrap/0.5_BOOTSTRAP/20_core-addons/20_cert_manager.sh <cluster> <region> [namespace]

bash bootstrap/0.5_BOOTSTRAP/30_platform-tooling/10_argocd_apps.sh <env>
bash bootstrap/0.5_BOOTSTRAP/30_platform-tooling/20_kong_ingress.sh <cluster> <region> [namespace]

bash bootstrap/0.5_BOOTSTRAP/40_smoke-tests/10_kubeconfig.sh <cluster> <region>
bash bootstrap/0.5_BOOTSTRAP/40_smoke-tests/20_audit.sh <cluster> <region>
```

## Post-build sanity checks

```
kubectl get nodes
kubectl top nodes
kubectl -n argocd get applications
kubectl -n kong get svc
```

## SSH break-glass

Node access uses SSM by default. Enable SSH break-glass only when needed.

```
terraform -chdir=envs/dev apply -var="enable_ssh_break_glass=true" -var="ssh_key_name=mikeybeezy" -var='ssh_source_security_group_ids=["sg-..."]'
```

Note: `ssh_key_name` is the AWS EC2 key pair name (not the local `.pem` file).

## Core add-ons (current)

Installed as EKS managed add-ons during cluster provisioning:

- coredns: cluster DNS for service discovery.
- kube-proxy: Kubernetes service networking on each node.
- vpc-cni: pod networking in the VPC (ENI/IP assignment).
- aws-ebs-csi-driver: block storage for persistent volumes.
- aws-efs-csi-driver: shared file storage for persistent volumes.
- snapshot-controller: CSI volume snapshot APIs.

## Private subnets and NAT requirement

EKS nodes run in private subnets. They must be able to reach public AWS
endpoints (EKS API, STS, ECR) to join the cluster. Private subnets need a
route to a NAT gateway in a public subnet. Without NAT (or VPC endpoints), node
nodes will fail to join and add-ons like CoreDNS will stay degraded.

## Failure recovery (imports)

If a cluster already exists (created outside this Terraform state), import the
existing node group and add-ons before applying. For a new cluster created by
Terraform, no imports are needed.

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

## Connect to the cluster

```
aws eks update-kubeconfig --region <region> --name <cluster>
kubectl get nodes
```

## Script references

- `cleanup-orphans.sh`: cleanup tagged orphaned resources (manual, dry-run default).
- `pre-destroy-cleanup.sh`: delete LoadBalancer services before teardown.
- `drain-nodegroup.sh`: cordon and drain nodes for safe node group updates.

## Kong notes

Kong is installed through Argo CD so the cluster reconciles with Git state.
Ingress strategy (Kong+NLB vs ALB): `docs/08_INGRESS_STRATEGY.md`.

## Argo CD access (Keycloak + admin bootstrap)

Argo CD admin access is for bootstrap only and should be disabled once SSO is
working. Use the helper script:

```
bootstrap/0.5_BOOTSTRAP/10_gitops-controller/20_argocd_admin_access.sh disable
bootstrap/0.5_BOOTSTRAP/10_gitops-controller/20_argocd_admin_access.sh enable
```
