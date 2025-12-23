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
- aws-ebs-csi-driver: block storage for persistent volumes.
- aws-efs-csi-driver: shared file storage for persistent volumes.
- snapshot-controller: CSI volume snapshot APIs.

## Strategy to move add-ons into 20_core-addons/

Short term we use EKS managed add-ons for fast, reliable cluster bring-up.
Longer term, once GitOps is the default, we will shift add-on ownership into
`20_core-addons/` and manage them declaratively (Helm/Kustomize) with version
pinning and configuration overrides. Terraform will keep cluster and node
infrastructure concerns only, while GitOps will manage add-on lifecycle.
