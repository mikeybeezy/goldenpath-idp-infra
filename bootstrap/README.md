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
```

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

## Bootstrap components (mandatory vs optional)

Mandatory (baseline cluster functionality):
- metrics-server: resource metrics API for `kubectl top` and autoscaling.
- vpc-cni: pod networking in the VPC (ENI/IP assignment).
- coredns: cluster DNS for service discovery.
- kube-proxy: Kubernetes service networking on each node.

Optional (platform capabilities):
- cluster-autoscaler or Karpenter: scales node groups or provisions nodes for pending pods.
- aws-load-balancer-controller: provisions ALB/NLB for Services/Ingress in AWS.
- external-dns: automates DNS records (e.g., Route53) for Services/Ingress.
- cert-manager: automates TLS certificates (e.g., Let’s Encrypt).
- ingress-nginx: NGINX Ingress controller; we plan to use Kong but keep nginx/traefik as alternatives.
- node-local-dns: per-node DNS cache to reduce CoreDNS load and speed lookups.
- calico: consider in v2 if we need NetworkPolicy enforcement or advanced networking features.
