# AGENT_CONTEXT: Read .agent/README.md for rules
terraform {
  required_version = ">= 1.5.0"
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

module "iam" {
  source = "../../modules/aws_iam"
  count  = var.iam_config.enabled ? 1 : 0

  # NOTE: cluster_role_name and node_group_role_name removed.
  # EKS cluster and node group IAM roles are created by the EKS module.
  enable_oidc_role                        = true
  oidc_role_name                          = "${var.iam_config.oidc_role_name}${local.role_suffix}"
  oidc_issuer_url                         = var.iam_config.oidc_issuer_url
  oidc_provider_arn                       = var.iam_config.oidc_provider_arn
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
  enable_eso_role                         = var.iam_config.enable_eso_role
  eso_role_name                           = "${var.iam_config.eso_role_name}${local.role_suffix}"
  eso_service_account_namespace           = var.iam_config.eso_service_account_namespace
  eso_service_account_name                = var.iam_config.eso_service_account_name
  enable_external_dns_role                = var.iam_config.enable_external_dns_role
  external_dns_role_name                  = "${var.iam_config.external_dns_role_name}${local.role_suffix}"
  external_dns_policy_arn                 = var.iam_config.external_dns_policy_arn
  external_dns_service_account_namespace  = var.iam_config.external_dns_service_account_namespace
  external_dns_service_account_name       = var.iam_config.external_dns_service_account_name
  external_dns_zone_id                    = var.route53_config.zone_id
  environment                             = local.environment
  tags                                    = local.common_tags
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

/*module "eks" {
  source = "../../modules/aws_eks"
  count  = var.eks_config.enabled ? 1 : 0

  cluster_name       = var.eks_config.cluster_name
  kubernetes_version = var.eks_config.version
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.subnets.private_subnet_ids
  node_group_config  = local.effective_node_group
  environment        = local.environment
  tags               = local.common_tags

  depends_on = [module.public_route_table]
}*/

################################################################################
# Managed Kubernetes Resources (ESO / Add-ons)
################################################################################

data "aws_eks_cluster" "this" {
  count = var.eks_config.enabled ? 1 : 0
  name  = local.cluster_name_effective
}

data "aws_eks_cluster_auth" "this" {
  count = var.eks_config.enabled ? 1 : 0
  name  = local.cluster_name_effective
}

locals {
  k8s_host    = try(data.aws_eks_cluster.this[0].endpoint, "https://localhost")
  k8s_ca_cert = try(base64decode(data.aws_eks_cluster.this[0].certificate_authority[0].data), "")
  k8s_token   = try(data.aws_eks_cluster_auth.this[0].token, "")
}

provider "kubernetes" {
  host                   = local.k8s_host
  cluster_ca_certificate = local.k8s_ca_cert
  token                  = local.k8s_token
}

provider "helm" {
  kubernetes {
    host                   = local.k8s_host
    cluster_ca_certificate = local.k8s_ca_cert
    token                  = local.k8s_token
  }
}

resource "kubernetes_service_account_v1" "external_secrets" {
  count = var.enable_k8s_resources && var.iam_config.enabled && var.iam_config.enable_eso_role ? 1 : 0

  metadata {
    name      = var.iam_config.eso_service_account_name
    namespace = var.iam_config.eso_service_account_namespace
    annotations = {
      "eks.amazonaws.com/role-arn" = module.iam[0].eso_role_arn
    }
  }

  depends_on = [
    module.iam
  ]
}

resource "kubernetes_service_account_v1" "external_dns" {
  count = var.enable_k8s_resources && var.iam_config.enabled && var.iam_config.enable_external_dns_role ? 1 : 0

  metadata {
    name      = var.iam_config.external_dns_service_account_name
    namespace = var.iam_config.external_dns_service_account_namespace
    annotations = {
      "eks.amazonaws.com/role-arn" = module.iam[0].external_dns_role_arn
    }
  }

  depends_on = [
    module.iam
  ]
}

resource "kubernetes_ingress_class_v1" "kong" {
  count = var.enable_k8s_resources ? 1 : 0

  metadata {
    name = "kong"
  }

  spec {
    controller = "ingress-controllers.konghq.com/kong"
  }
}

module "app_secrets" {
  source = "../../modules/aws_secrets_manager"

  name        = "${local.name_prefix}-app-secrets"
  description = "Standard application secrets for ${local.environment}"
  tags        = local.common_tags

  metadata = {
    id    = "SECRET_PLATFORM_CORE_${upper(local.environment)}"
    owner = var.owner_team
    risk  = "medium"
  }
}

################################################################################
# S3 Buckets (Contract-Driven)
################################################################################

module "s3_bucket" {
  source = "../../modules/aws_s3"
  count  = var.s3_bucket == null ? 0 : 1

  bucket_name        = var.s3_bucket != null ? var.s3_bucket.bucket_name : ""
  versioning_enabled = var.s3_bucket != null ? var.s3_bucket.versioning_enabled : true
  encryption         = var.s3_bucket != null ? var.s3_bucket.encryption : { type = "SSE_S3" }
  public_access_block = var.s3_bucket != null ? var.s3_bucket.public_access_block : {
    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
  }
  lifecycle_rules = var.s3_bucket != null && var.s3_bucket.lifecycle_rules != null ? var.s3_bucket.lifecycle_rules : []
  logging         = var.s3_bucket != null ? var.s3_bucket.logging : null
  tags            = merge(local.common_tags, var.s3_bucket != null ? var.s3_bucket.tags : {})
  cost_alert      = var.cost_alert
}

module "kubernetes_addons" {
  source = "../../modules/kubernetes_addons"
  count  = var.eks_config.enabled && var.enable_k8s_resources ? 1 : 0

  path_to_app_manifests = "${path.module}/../../gitops/argocd/apps/${local.environment}"
  argocd_values         = file("${path.module}/../../gitops/helm/argocd/values/${local.environment}.yaml")

  # AWS Load Balancer Controller specific inputs
  vpc_id       = module.vpc.vpc_id
  cluster_name = local.cluster_name_effective
  aws_region   = var.aws_region

  tags = local.common_tags

  # Since EKS is commented out in this tier, we don't add it to depends_on for now
  # but we keep the logic ready.
  depends_on = [
    kubernetes_service_account_v1.external_secrets,
    kubernetes_service_account_v1.external_dns,
    kubernetes_ingress_class_v1.kong,
  ]
}
