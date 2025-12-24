# EKS Cluster Module

## Purpose
Creates an EKS cluster, a managed node group, a cluster security group, IAM
roles, and an OIDC provider. Installs core add-ons and optionally storage
add-ons.

## Inputs
- `cluster_name` (string): Cluster name.
- `kubernetes_version` (string): EKS version.
- `vpc_id` (string): VPC ID.
- `subnet_ids` (list(string)): Subnets for cluster/node group.
- `node_group_config` (object): Node group sizing and instance config.
- `access_config` (object, optional): Auth mode and bootstrap permissions.
- `enable_ssh_break_glass` (bool, optional): Enable SSH access.
- `ssh_key_name` (string, optional): EC2 key pair name for SSH.
- `ssh_source_security_group_ids` (list(string), optional): Allowed SSH SGs.
- `addon_versions` (map(string), optional): Pin add-on versions.
- `addon_replica_counts` (map(number), optional): Replica counts for add-ons.
- `enable_storage_addons` (bool, optional): Enable EBS/EFS/snapshot add-ons.
- `tags` (map(string), optional): Tags for resources.
- `environment` (string, optional): Environment tag.

## Outputs
- `cluster_name`
- `cluster_endpoint`
- `cluster_security_group_id`
- `cluster_ca`
- `node_group_name`
- `node_group_role_arn`
- `oidc_issuer_url`
- `oidc_provider_arn`

## Notes
- Creates cluster and node IAM roles internally.
- Core add-ons: `coredns`, `kube-proxy`, `vpc-cni`.
- Storage add-ons are gated by `enable_storage_addons`.

## Failure modes
- Private subnets missing NAT/endpoint routing (nodes fail to join).
- Insufficient IAM permissions for EKS and IAM roles.
