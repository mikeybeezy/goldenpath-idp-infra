terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12"
    }
  }
}

locals {
  environment            = var.environment
  cluster_lifecycle      = var.cluster_lifecycle
  build_id               = var.build_id
  base_name_prefix       = var.name_prefix != "" ? var.name_prefix : "goldenpath-${local.environment}"
  name_prefix            = local.cluster_lifecycle == "ephemeral" && local.build_id != "" ? "${local.base_name_prefix}-${local.build_id}" : local.base_name_prefix
  cluster_name           = var.eks_config.cluster_name != "" ? var.eks_config.cluster_name : "${local.base_name_prefix}-eks"
  cluster_name_effective = local.cluster_lifecycle == "ephemeral" && local.build_id != "" ? "${local.cluster_name}-${local.build_id}" : local.cluster_name
  role_suffix            = local.cluster_lifecycle == "ephemeral" && local.build_id != "" ? "-${local.build_id}" : ""
  public_subnets         = var.public_subnets
  private_subnets        = var.private_subnets
  # Use a larger node group during bootstrap to avoid capacity bottlenecks.
  effective_node_group = var.bootstrap_mode ? merge(
    var.eks_config.node_group,
    {
      min_size     = var.bootstrap_node_group.min_size
      desired_size = var.bootstrap_node_group.desired_size
      max_size     = var.bootstrap_node_group.max_size
    }
  ) : var.eks_config.node_group

  common_tags = merge(
    {
      Environment = local.environment
      Project     = "goldenpath-idp"
      ManagedBy   = "terraform"
      Owner       = var.owner_team
      Lifecycle   = local.cluster_lifecycle
    },
    local.build_id != "" ? { BuildId = local.build_id } : {},
    var.common_tags,
  )
}

module "vpc" {
  source = "../../modules/vpc"

  vpc_cidr    = var.vpc_cidr
  vpc_tag     = "${local.name_prefix}-vpc"
  environment = local.environment
  tags        = local.common_tags
}

module "subnets" {
  source = "../../modules/aws_subnet"

  vpc_id          = module.vpc.vpc_id
  public_subnets  = local.public_subnets
  private_subnets = local.private_subnets
  environment     = local.environment
  tags            = local.common_tags
}

module "iam" {
  source = "../../modules/aws_iam"
  count  = var.iam_config.enabled ? 1 : 0

  cluster_role_name                       = "${var.iam_config.cluster_role_name != "" ? var.iam_config.cluster_role_name : "${local.base_name_prefix}-eks-cluster-role"}${local.role_suffix}"
  node_group_role_name                    = "${var.iam_config.node_group_role_name != "" ? var.iam_config.node_group_role_name : "${local.base_name_prefix}-eks-node-role"}${local.role_suffix}"
  oidc_role_name                          = "${var.iam_config.oidc_role_name != "" ? var.iam_config.oidc_role_name : "${local.base_name_prefix}-eks-oidc-role"}${local.role_suffix}"
  oidc_issuer_url                         = module.eks[0].oidc_issuer_url
  oidc_provider_arn                       = module.eks[0].oidc_provider_arn
  oidc_audience                           = var.iam_config.oidc_audience
  oidc_subject                            = var.iam_config.oidc_subject
  enable_autoscaler_role                  = var.iam_config.enable_autoscaler_role
  autoscaler_role_name                    = "${var.iam_config.autoscaler_role_name}${local.role_suffix}"
  autoscaler_policy_arn                   = var.iam_config.autoscaler_policy_arn
  autoscaler_service_account_namespace    = var.iam_config.autoscaler_service_account_namespace
  autoscaler_service_account_name         = var.iam_config.autoscaler_service_account_name
  enable_lb_controller_role               = var.iam_config.enable_lb_controller_role
  lb_controller_role_name                 = "${var.iam_config.lb_controller_role_name}${local.role_suffix}"
  lb_controller_policy_arn                = var.iam_config.lb_controller_policy_arn
  lb_controller_service_account_namespace = var.iam_config.lb_controller_service_account_namespace
  lb_controller_service_account_name      = var.iam_config.lb_controller_service_account_name
  environment                             = local.environment
  tags                                    = local.common_tags

  depends_on = [module.eks]
}

module "public_route_table" {
  source = "../../modules/aws_route_table"

  vpc_id                 = module.vpc.vpc_id
  name                   = "${local.name_prefix}-public-rt"
  gateway_id             = module.vpc.internet_gateway_id
  subnet_ids             = module.subnets.public_subnet_ids
  destination_cidr_block = "0.0.0.0/0"
  environment            = local.environment
  tags                   = local.common_tags
}

resource "aws_eip" "nat" {
  domain = "vpc"

  tags = merge(
    {
      Name = "${local.name_prefix}-nat-eip"
    },
    local.common_tags,
  )
}

resource "aws_nat_gateway" "this" {
  allocation_id = aws_eip.nat.id
  subnet_id     = element(module.subnets.public_subnet_ids, 0)

  tags = merge(
    {
      Name = "${local.name_prefix}-nat"
    },
    local.common_tags,
  )
}

module "private_route_table" {
  source = "../../modules/aws_route_table"

  vpc_id                 = module.vpc.vpc_id
  name                   = "${local.name_prefix}-private-rt"
  nat_gateway_id         = aws_nat_gateway.this.id
  subnet_ids             = module.subnets.private_subnet_ids
  destination_cidr_block = "0.0.0.0/0"
  environment            = local.environment
  tags                   = local.common_tags
}

module "web_security_group" {
  source = "../../modules/aws_sg"

  name                     = "${local.name_prefix}-web-sg"
  vpc_id                   = module.vpc.vpc_id
  ingress_cidr_blocks      = ["0.0.0.0/0"]
  ingress_ipv6_cidr_blocks = ["::/0"]
  environment              = local.environment
  tags                     = local.common_tags
}

module "compute" {
  source = "../../modules/aws_compute"
  count  = var.compute_config.enabled ? 1 : 0

  name                          = var.compute_config.name
  ami_id                        = var.compute_config.ami_id
  instance_type                 = var.compute_config.instance_type
  subnet_id                     = var.compute_config.subnet_type == "public" ? element(module.subnets.public_subnet_ids, 0) : element(module.subnets.private_subnet_ids, 0)
  security_group_ids            = concat([module.web_security_group.security_group_id], var.compute_config.additional_security_group_ids)
  ssh_key_name                  = var.compute_config.ssh_key_name
  user_data                     = var.compute_config.user_data
  iam_instance_profile          = var.compute_config.iam_instance_profile
  network_interface_description = var.compute_config.network_interface_description
  root_volume_size              = var.compute_config.root_volume_size
  root_volume_type              = var.compute_config.root_volume_type
  root_volume_encrypted         = var.compute_config.root_volume_encrypted
  environment                   = local.environment
  tags                          = local.common_tags
}

module "eks" {
  source = "../../modules/aws_eks"
  count  = var.eks_config.enabled ? 1 : 0

  cluster_name                  = local.cluster_name_effective
  kubernetes_version            = var.eks_config.version
  vpc_id                        = module.vpc.vpc_id
  subnet_ids                    = module.subnets.private_subnet_ids
  node_group_config             = local.effective_node_group
  addon_replica_counts          = var.addon_replica_counts
  enable_storage_addons         = var.enable_storage_addons
  enable_ssh_break_glass        = var.enable_ssh_break_glass
  ssh_key_name                  = var.ssh_key_name
  ssh_source_security_group_ids = var.ssh_source_security_group_ids
  environment                   = local.environment
  tags                          = local.common_tags

  depends_on = [module.public_route_table]
}

data "aws_eks_cluster_auth" "this" {
  name = module.eks[0].cluster_name
}

provider "kubernetes" {
  host                   = module.eks[0].cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks[0].cluster_ca)
  token                  = data.aws_eks_cluster_auth.this.token
}

resource "kubernetes_service_account_v1" "aws_load_balancer_controller" {
  count = var.enable_k8s_resources && var.iam_config.enabled && var.iam_config.enable_lb_controller_role ? 1 : 0

  metadata {
    name      = var.iam_config.lb_controller_service_account_name
    namespace = var.iam_config.lb_controller_service_account_namespace
    annotations = {
      "eks.amazonaws.com/role-arn" = module.iam[0].lb_controller_role_arn
    }
  }

  depends_on = [module.eks, module.iam]
}



provider "helm" {
  kubernetes {
    host                   = module.eks[0].cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks[0].cluster_ca)
    token                  = data.aws_eks_cluster_auth.this.token
  }
}

module "kubernetes_addons" {
  source = "../../modules/kubernetes_addons"
  count  = var.eks_config.enabled ? 1 : 0

  path_to_app_manifests = "${path.module}/../../gitops/argocd/apps/dev"

  tags = local.common_tags

  depends_on = [module.eks]
}
