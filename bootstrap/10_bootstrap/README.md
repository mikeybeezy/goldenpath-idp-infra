# Bootstrap Entrypoint

This directory is the single entrypoint that answers: how does a blank cluster
become a platform? It captures the intended bootstrap flow and the boundary
between cluster creation and platform rollout.

bootstrap/10_bootstrap/
  README.md
  00_prereqs/
  10_gitops-controller/
  30_core-addons/
  40_platform-tooling/
  50_smoke-tests/
  goldenpath-idp-bootstrap.sh
  60_tear_down_clean_up/cleanup-orphans.sh
  60_tear_down_clean_up/pre-destroy-cleanup.sh
  60_tear_down_clean_up/drain-nodegroup.sh
  one_stage_vs_multistage_bootstrap.md

## Recommended sequence

1) 00_prereqs: verify required tools are installed and run EKS preflight.
2) 50_smoke-tests: install Metrics Server and validate node metrics.
3) 10_gitops-controller: install Argo CD via Helm.
4) 30_core-addons: validate AWS LB Controller and cert-manager.
5) 40_platform-tooling: apply Argo CD apps, optionally wait for autoscaler, then validate Kong ingress.
6) 50_smoke-tests: run the audit report.
7) Optional: scale down after bootstrap.
8) 50_smoke-tests: sanity checklist and final status summary.

Argo CD is where the cluster reconciles against the desired state in this repo.
Once Applications are created, Argo CD keeps them in sync with Git.
GitOps details live in `docs/12_GITOPS_AND_CICD.md`.

At the end of the runner, we print an Argo status summary. If any app reports
`HEALTH=Unknown`, the runner prints a warning so you can review it manually.

## Flow diagram (quick view)

```
Prereqs
  -> Metrics Server
  -> Argo CD
  -> Core add-ons (LB controller, cert-manager)
  -> Argo apps (autoscaler + tooling)
  -> Kong validation
  -> Audit report
  -> Optional scale down
  -> Sanity checklist
  -> Bootstrap complete
```

## One-stage vs multi-stage

Guidance and use cases are in:
`bootstrap/10_bootstrap/one_stage_vs_multistage_bootstrap.md`

## Prereqs (mandatory)

```
bootstrap/00_prereqs/00_check_tools.sh
bootstrap/00_prereqs/10_eks_preflight.sh <cluster> <region> <vpc-id> <private-subnet-ids> <node-role-arn> <instance-type>
```

## Bootstrap runner (recommended)

```
NODE_INSTANCE_TYPE=t3.small bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh <cluster> <region> [kong-namespace]
```

Bootstrap mode defaults for this environment:

- `bootstrap_mode` = `true`
- `min_size` = 3
- `desired_size` = 3
- `max_size` = 5
- `enable_ssh_break_glass` = `false`

Optional scale-down after bootstrap:

```
NODE_INSTANCE_TYPE=t3.small SCALE_DOWN_AFTER_BOOTSTRAP=true TF_DIR=goldenpath-idp-infra/envs/dev \
  bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh <cluster> <region>
```

Skip cert-manager validation (default behavior):

```
SKIP_CERT_MANAGER_VALIDATION=true NODE_INSTANCE_TYPE=t3.small ENV_NAME=dev \
  bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh <cluster> <region>
```

Skip waiting for Argo CD apps to sync (default behavior):

```
SKIP_ARGO_SYNC_WAIT=true NODE_INSTANCE_TYPE=t3.small ENV_NAME=dev \
  bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh <cluster> <region>
```

Enable compact output (reduces noisy command output, keeps stage banners and warnings):

```
COMPACT_OUTPUT=true NODE_INSTANCE_TYPE=t3.small ENV_NAME=dev \
  bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh <cluster> <region>
```

### Example: compact output (`COMPACT_OUTPUT=true`)

```
Bootstrap starting for cluster goldenpath-dev-eks in eu-west-2

##### STAGE 1: CLUSTER CONTEXT #####
Updating kubeconfig for goldenpath-dev-eks (eu-west-2)...
----- STAGE 1 DONE -----

##### STAGE 2: TOOL CHECKS #####
Checking required tools...
----- STAGE 2 DONE -----

##### STAGE 3: EKS PREFLIGHT #####
Running EKS preflight...
----- STAGE 3 DONE -----

##### STAGE 4: CAPACITY CHECK #####
Checking Ready node count...
----- STAGE 4 DONE -----

##### STAGE 5: METRICS SERVER #####
Installing Metrics Server...
----- STAGE 5 DONE -----

##### STAGE 6: ARGO CD #####
INSTALLING Argo CD...
----- STAGE 6 DONE -----

##### STAGE 7: CORE ADD-ONS #####
INSTALLING AWS Load Balancer Controller...
Skipping cert-manager validation; Argo apps may not be synced yet.
----- STAGE 7 DONE -----

##### STAGE 8: PLATFORM APPS #####
INSTALLING Argo apps for dev...
----- STAGE 8 DONE -----
Skipping Argo CD sync wait (SKIP_ARGO_SYNC_WAIT=true).

##### STAGE 9: AUTOSCALER #####
Checking Cluster Autoscaler rollout...
Error from server (NotFound): deployments.apps "cluster-autoscaler" not found
Warning: cluster-autoscaler deployment not ready yet.
----- STAGE 9 DONE -----

##### STAGE 10: KONG #####
VALIDATING Kong ingress...
----- STAGE 10 DONE -----

##### STAGE 11: AUDIT #####
Running audit checks...
----- STAGE 11 DONE -----

##### STAGE 12: OPTIONAL SCALE DOWN #####
Skipping scale down (SCALE_DOWN_AFTER_BOOTSTRAP=false).
----- STAGE 12 DONE -----
Bootstrap complete.
Sanity checks:
  kubectl get nodes
  kubectl top nodes
  kubectl -n argocd get applications
  kubectl -n kong-system get svc
NAME                     SYNC        HEALTH        MESSAGE
dev-alertmanager         Synced      Progressing   <none>
dev-backstage            Unknown     Healthy       <none>
dev-cert-manager         Synced      Progressing   <none>
dev-cluster-autoscaler   Synced      Healthy       <none>
dev-datree               Unknown     Healthy       <none>
dev-external-secrets     Synced      Healthy       <none>
dev-fluent-bit           Synced      Healthy       <none>
dev-grafana              Synced      Healthy       <none>
dev-keycloak             Unknown     Healthy       <none>
dev-kong                 OutOfSync   Healthy       <none>
dev-loki                 Synced      Healthy       <none>
dev-prometheus           Synced      Degraded      <none>
```

### Example: full output (`COMPACT_OUTPUT=false`)

```
Bootstrap starting for cluster goldenpath-dev-eks in eu-west-2
Updated context arn:aws:eks:eu-west-2:593517239005:cluster/goldenpath-dev-eks in /Users/mikesablaze/.kube/config
aws-cli/1.33.35 Python/3.11.0 Darwin/23.6.0 botocore/1.34.153
Client Version: v1.32.3
Kustomize Version: v5.5.0
version.BuildInfo{Version:"v3.10.3", GitCommit:"835b7334cfe2e5e27870ab3ed4135f136eecc704", GitTreeState:"clean", GoVersion:"go1.19.4"}
Preflight checks for goldenpath-dev-eks in eu-west-2
Cluster endpoint public=True private=False
Checking NAT routes for private subnets...
Checking node IAM role policies...
Checking instance type availability: t3.small
Ready nodes: 4
Preflight checks passed.
Updated context arn:aws:eks:eu-west-2:593517239005:cluster/goldenpath-dev-eks in /Users/mikesablaze/.kube/config
NAME                                        STATUS   ROLES    AGE   VERSION
ip-10-0-11-101.eu-west-2.compute.internal   Ready    <none>   86m   v1.29.15-eks-ecaa3a6
ip-10-0-11-213.eu-west-2.compute.internal   Ready    <none>   63m   v1.29.15-eks-ecaa3a6
ip-10-0-12-6.eu-west-2.compute.internal     Ready    <none>   86m   v1.29.15-eks-ecaa3a6
ip-10-0-12-8.eu-west-2.compute.internal     Ready    <none>   86m   v1.29.15-eks-ecaa3a6
serviceaccount/metrics-server unchanged
clusterrole.rbac.authorization.k8s.io/system:aggregated-metrics-reader unchanged
clusterrole.rbac.authorization.k8s.io/system:metrics-server unchanged
rolebinding.rbac.authorization.k8s.io/metrics-server-auth-reader unchanged
clusterrolebinding.rbac.authorization.k8s.io/metrics-server:system:auth-delegator unchanged
clusterrolebinding.rbac.authorization.k8s.io/system:metrics-server unchanged
service/metrics-server unchanged
deployment.apps/metrics-server configured
apiservice.apiregistration.k8s.io/v1beta1.metrics.k8s.io unchanged
deployment "metrics-server" successfully rolled out
NAME                                        CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)
ip-10-0-11-101.eu-west-2.compute.internal   67m          3%       1064Mi          72%
ip-10-0-11-213.eu-west-2.compute.internal   44m          2%       825Mi           56%
ip-10-0-12-6.eu-west-2.compute.internal     68m          3%       870Mi           59%
ip-10-0-12-8.eu-west-2.compute.internal     64m          3%       782Mi           53%
Updated context arn:aws:eks:eu-west-2:593517239005:cluster/goldenpath-dev-eks in /Users/mikesablaze/.kube/config
"argo" already exists with the same configuration, skipping
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "coredns" chart repository
...Successfully got an update from the "ingress-nginx" chart repository
...Successfully got an update from the "kong" chart repository
...Successfully got an update from the "eks" chart repository
...Successfully got an update from the "jetstack" chart repository
...Successfully got an update from the "argo" chart repository
...Successfully got an update from the "prometheus" chart repository
...Successfully got an update from the "prometheus-community" chart repository
...Successfully got an update from the "bitnami" chart repository
Update Complete. ⎈Happy Helming!⎈
namespace/argocd configured
Release "argocd" has been upgraded. Happy Helming!
NAME: argocd
LAST DEPLOYED: Wed Dec 24 12:17:06 2025
NAMESPACE: argocd
STATUS: deployed
REVISION: 4
TEST SUITE: None
NOTES:
In order to access the server UI you have the following options:

1. kubectl port-forward service/argocd-server -n argocd 8080:443

    and then open the browser on http://localhost:8080 and accept the certificate

2. enable ingress in the values file `server.ingress.enabled` and either
      - Add the annotation for ssl passthrough: https://argo-cd.readthedocs.io/en/stable/operator-manual/ingress/#option-1-ssl-passthrough
      - Set the `configs.params."server.insecure"` in the values file and terminate SSL at your ingress: https://argo-cd.readthedocs.io/en/stable/operator-manual/ingress/#option-2-multiple-ingress-objects-and-hosts


After reaching the UI the first time you can login with username: admin and the random password generated during the installation. You can find the password by running:

kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

(You should delete the initial secret afterwards as suggested by the Getting Started Guide: https://argo-cd.readthedocs.io/en/stable/getting_started/#4-login-using-the-cli)
deployment "argocd-server" successfully rolled out
NAME                               TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)             AGE
argocd-applicationset-controller   ClusterIP   172.20.39.224    <none>        7000/TCP            65m
argocd-dex-server                  ClusterIP   172.20.53.115    <none>        5556/TCP,5557/TCP   65m
argocd-redis                       ClusterIP   172.20.52.130    <none>        6379/TCP            65m
argocd-repo-server                 ClusterIP   172.20.23.61     <none>        8081/TCP            65m
argocd-server                      ClusterIP   172.20.173.171   <none>        80/TCP,443/TCP      65m
Updated context arn:aws:eks:eu-west-2:593517239005:cluster/goldenpath-dev-eks in /Users/mikesablaze/.kube/config
"eks" already exists with the same configuration, skipping
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "coredns" chart repository
...Successfully got an update from the "jetstack" chart repository
...Successfully got an update from the "ingress-nginx" chart repository
...Successfully got an update from the "kong" chart repository
...Successfully got an update from the "eks" chart repository
...Successfully got an update from the "argo" chart repository
...Successfully got an update from the "prometheus-community" chart repository
...Successfully got an update from the "prometheus" chart repository
...Successfully got an update from the "bitnami" chart repository
Update Complete. ⎈Happy Helming!⎈
Release "aws-load-balancer-controller" has been upgraded. Happy Helming!
NAME: aws-load-balancer-controller
LAST DEPLOYED: Wed Dec 24 12:17:28 2025
NAMESPACE: kube-system
STATUS: deployed
REVISION: 4
TEST SUITE: None
NOTES:
AWS Load Balancer controller installed!
deployment "aws-load-balancer-controller" successfully rolled out
Skipping cert-manager validation; Argo apps may not be synced yet.
application.argoproj.io/dev-alertmanager unchanged
application.argoproj.io/dev-backstage unchanged
application.argoproj.io/dev-cert-manager unchanged
application.argoproj.io/dev-cluster-autoscaler unchanged
application.argoproj.io/dev-datree unchanged
application.argoproj.io/dev-external-secrets unchanged
application.argoproj.io/dev-fluent-bit unchanged
application.argoproj.io/dev-grafana unchanged
application.argoproj.io/dev-keycloak unchanged
application.argoproj.io/dev-kong unchanged
application.argoproj.io/dev-loki unchanged
application.argoproj.io/dev-prometheus unchanged
NAME                     SYNC STATUS   HEALTH STATUS
dev-alertmanager         Synced        Progressing
dev-backstage            Unknown       Healthy
dev-cert-manager         Synced        Healthy
dev-cluster-autoscaler   Synced        Healthy
dev-datree               Unknown       Healthy
dev-external-secrets     Synced        Healthy
dev-fluent-bit           Synced        Healthy
dev-grafana              Synced        Healthy
dev-keycloak             Unknown       Healthy
dev-kong                 OutOfSync     Healthy
dev-loki                 Synced        Healthy
dev-prometheus           Synced        Degraded
Skipping Argo CD sync wait (SKIP_ARGO_SYNC_WAIT=true).
Error from server (NotFound): deployments.apps "cluster-autoscaler" not found
Warning: cluster-autoscaler deployment not ready yet.
Updated context arn:aws:eks:eu-west-2:593517239005:cluster/goldenpath-dev-eks in /Users/mikesablaze/.kube/config
deployment "dev-kong-kong" successfully rolled out
NAME                               TYPE           CLUSTER-IP       EXTERNAL-IP                                                                     PORT(S)                         AGE
dev-kong-kong-manager              NodePort       172.20.219.171   <none>                                                                          8002:31284/TCP,8445:30645/TCP   64m
dev-kong-kong-metrics              ClusterIP      172.20.124.230   <none>                                                                          10255/TCP,10254/TCP             64m
dev-kong-kong-proxy                LoadBalancer   172.20.244.13    k8s-kongsyst-devkongk-bbc576901d-bed406492f6151bf.elb.eu-west-2.amazonaws.com   80:32090/TCP,443:30845/TCP      64m
dev-kong-kong-validation-webhook   ClusterIP      172.20.147.77    <none>                                                                          443/TCP                         64m
Audit written to bootstrap/50_smoke-tests/audit/goldenpath-dev-eks-20251224T121735Z.md
Bootstrap complete.
Sanity checks:
  kubectl get nodes
  kubectl top nodes
  kubectl -n argocd get applications
  kubectl -n kong-system get svc
NAME                     SYNC        HEALTH        MESSAGE
dev-alertmanager         Synced      Progressing   <none>
dev-backstage            Unknown     Healthy       <none>
dev-cert-manager         Synced      Healthy       <none>
dev-cluster-autoscaler   Synced      Healthy       <none>
dev-datree               Unknown     Healthy       <none>
dev-external-secrets     Synced      Healthy       <none>
dev-fluent-bit           Synced      Healthy       <none>
dev-grafana              Synced      Healthy       <none>
dev-keycloak             Unknown     Healthy       <none>
dev-kong                 OutOfSync   Healthy       <none>
dev-loki                 Synced      Healthy       <none>
dev-prometheus           Synced      Degraded      <none>
```

This mode is best when you are debugging a specific failure and want full
command output.

Enforce cert-manager validation after Argo apps sync:

```
SKIP_CERT_MANAGER_VALIDATION=false NODE_INSTANCE_TYPE=t3.small ENV_NAME=dev \
  bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh <cluster> <region>
```

## Full manual sequence (multi-stage)

```
bash bootstrap/00_prereqs/00_check_tools.sh
bash bootstrap/00_prereqs/10_eks_preflight.sh <cluster> <region> <vpc-id> <private-subnet-ids> <node-role-arn> <instance-type>

bash bootstrap/50_smoke-tests/10_kubeconfig.sh <cluster> <region>

bash bootstrap/10_gitops-controller/10_argocd_helm.sh <cluster> <region> [values_file]

bash bootstrap/30_core-addons/10_aws_lb_controller.sh <cluster> <region> <vpc_id> [service_account_name] [service_account_namespace]
bash bootstrap/30_core-addons/20_cert_manager.sh <cluster> <region> [namespace]  # Optional until Argo apps are synced

bash bootstrap/40_platform-tooling/10_argocd_apps.sh <env>
# Ensure cluster-autoscaler is running before Kong.
kubectl -n kube-system rollout status deployment/cluster-autoscaler --timeout=180s
bash bootstrap/40_platform-tooling/20_kong_ingress.sh <cluster> <region> [namespace]

bash bootstrap/50_smoke-tests/20_audit.sh <cluster> <region>
```

## Post-build sanity checks

```
kubectl get nodes
kubectl top nodes
kubectl -n argocd get applications
kubectl -n kong-system get svc
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

Note: EBS/EFS/snapshot add-ons can be disabled via `enable_storage_addons=false`
and enabled later once the cluster is stable.

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

- `60_tear_down_clean_up/cleanup-orphans.sh`: cleanup tagged orphaned resources (manual, dry-run default).
- `60_tear_down_clean_up/pre-destroy-cleanup.sh`: delete LoadBalancer services before teardown.
- `60_tear_down_clean_up/drain-nodegroup.sh`: cordon and drain nodes for safe node group updates.
- Manual teardown commands: `docs/15_TEARDOWN_AND_CLEANUP.md`.

## Kong notes

Kong is installed through Argo CD so the cluster reconciles with Git state.
Ingress strategy (Kong+NLB vs ALB): `docs/08_INGRESS_STRATEGY.md`.
cert-manager is also installed through Argo CD. If Argo apps have not synced
yet, skip the cert-manager validation and re-run it after the apps are applied.

## Troubleshooting: Kong LoadBalancer pending

If `kubectl -n kong get svc` shows a `LoadBalancer` stuck in `pending`, the
AWS Load Balancer Controller likely lacks permissions. A common error is:
`UnauthorizedOperation: ec2:DescribeRouteTables`. Ensure the controller IAM
role includes `ec2:DescribeRouteTables`, then restart the deployment:

```
kubectl -n kube-system rollout restart deploy/aws-load-balancer-controller
```

## Argo CD access (Keycloak + admin bootstrap)

Argo CD admin access is for bootstrap only and should be disabled once SSO is
working. Use the helper script:

```
bootstrap/10_gitops-controller/20_argocd_admin_access.sh disable
bootstrap/10_gitops-controller/20_argocd_admin_access.sh enable
```
