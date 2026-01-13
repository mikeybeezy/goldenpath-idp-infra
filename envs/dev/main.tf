################################################################################
# Terraform Configuration & Providers
################################################################################

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
    external = {
      source  = "hashicorp/external"
      version = "~> 2.3"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

################################################################################
# Global Metadata & Dynamic Resource Naming
################################################################################

locals {
  environment       = var.environment
  cluster_lifecycle = var.cluster_lifecycle
  build_id          = var.build_id
  base_name_prefix  = var.name_prefix != "" ? var.name_prefix : "goldenpath-${local.environment}"

  # Dynamic naming: suffixes resources with BuildId if in ephemeral/CI mode
  name_prefix            = local.cluster_lifecycle == "ephemeral" && local.build_id != "" ? "${local.base_name_prefix}-${local.build_id}" : local.base_name_prefix
  cluster_name           = var.eks_config.cluster_name != "" ? var.eks_config.cluster_name : "${local.base_name_prefix}-eks"
  cluster_name_effective = local.cluster_lifecycle == "ephemeral" && local.build_id != "" ? "${local.cluster_name}-${local.build_id}" : local.cluster_name
  role_suffix            = local.cluster_lifecycle == "ephemeral" && local.build_id != "" ? "-${local.build_id}" : ""

  public_subnets  = var.public_subnets
  private_subnets = var.private_subnets

  # Inject larger node sizing if the cluster is in 'bootstrap_mode' to speed up bring-up
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

################################################################################
# Build ID Immutability Enforcement
################################################################################

# External data source to check if build_id exists in governance-registry
data "external" "build_id_check" {
  count   = var.cluster_lifecycle == "ephemeral" && var.build_id != "" ? 1 : 0
  program = ["bash", "-c", <<-EOT
    set -e
    BUILD_ID="${var.build_id}"
    ENV="${var.environment}"
    REGISTRY_BRANCH="${var.governance_registry_branch}"
    CSV_PATH="environments/development/latest/build_timings.csv"

    # Fetch latest CSV from governance-registry branch
    CSV_CONTENT=$(git show "origin/$REGISTRY_BRANCH:$CSV_PATH" 2>/dev/null || echo "")

    if [ -z "$CSV_CONTENT" ]; then
      echo '{"exists":"false","error":"Registry CSV not found or git fetch needed"}'
      exit 0
    fi

    # Check if build_id exists for this environment (skip header)
    if echo "$CSV_CONTENT" | grep -q ",$ENV,$BUILD_ID," 2>/dev/null; then
      echo '{"exists":"true","build_id":"'"$BUILD_ID"'","environment":"'"$ENV"'"}'
    else
      echo '{"exists":"false","build_id":"'"$BUILD_ID"'","environment":"'"$ENV"'"}'
    fi
  EOT
  ]
}

# Enforce build_id immutability via lifecycle precondition
resource "null_resource" "enforce_build_id_immutability" {
  count = var.cluster_lifecycle == "ephemeral" && var.build_id != "" ? 1 : 0

  lifecycle {
    precondition {
      condition     = !var.allow_build_id_reuse ? try(data.external.build_id_check[0].result.exists, "false") == "false" : true
      error_message = <<-EOT
        Build ID ${var.build_id} already exists for environment ${var.environment}.

        This build_id was previously used. To prevent state corruption and resource conflicts,
        you must use a unique build_id for each ephemeral cluster deployment.

        Options:
        1. Use a new build_id (recommended): Increment the sequence number
           Example: If current is ${var.build_id}, try incrementing the last segment
           ${substr(var.build_id, 0, 9)}${format("%02d", tonumber(substr(var.build_id, 9, 2)) + 1)}

        2. Override protection (NOT recommended, only for testing/recovery):
           terraform apply -var="build_id=${var.build_id}" -var="allow_build_id_reuse=true"

           WARNING: Reusing build_ids can cause:
           - Terraform state corruption (conflicting state keys)
           - Resource naming conflicts in AWS
           - Lost audit trail and compliance violations

        Check governance registry for existing builds:
        git show origin/${var.governance_registry_branch}:environments/development/latest/build_timings.csv
      EOT
    }
  }

  triggers = {
    build_id    = var.build_id
    environment = var.environment
  }
}

################################################################################
# Core Foundation: VPC & Networking
################################################################################

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

# NAT Gateway for private subnet outbound connectivity
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

################################################################################
# Compute & Standalone Instances
################################################################################

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

################################################################################
# Kubernetes Foundation: EKS Cluster
################################################################################

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

################################################################################
# Identity & Access Management (IAM)
################################################################################

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
  enable_eso_role                         = var.iam_config.enable_eso_role
  eso_role_name                           = "${var.iam_config.eso_role_name}${local.role_suffix}"
  eso_service_account_namespace           = var.iam_config.eso_service_account_namespace
  eso_service_account_name                = var.iam_config.eso_service_account_name
  environment                             = local.environment
  tags                                    = local.common_tags

  depends_on = [module.eks]
}

# Principal identity for bootstrapping admin access
data "aws_caller_identity" "current" {}

# Grant the Terraform runner (CI role or local user) admin access to the cluster
resource "aws_eks_access_entry" "terraform_admin" {
  cluster_name  = module.eks[0].cluster_name
  principal_arn = data.aws_caller_identity.current.arn
  type          = "STANDARD"

  tags = local.common_tags

  depends_on = [module.eks]
}

resource "aws_eks_access_policy_association" "terraform_admin" {
  cluster_name  = module.eks[0].cluster_name
  principal_arn = aws_eks_access_entry.terraform_admin.principal_arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type = "cluster"
  }

  depends_on = [aws_eks_access_entry.terraform_admin]
}

################################################################################
# Managed Kubernetes Resources (ESO / Add-ons)
################################################################################

provider "kubernetes" {
  host                   = module.eks[0].cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks[0].cluster_ca)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    args        = ["eks", "get-token", "--cluster-name", module.eks[0].cluster_name, "--region", var.aws_region]
    command     = "aws"
  }
}

resource "kubernetes_service_account_v1" "aws_load_balancer_controller" {
  count = var.eks_config.enabled && var.enable_k8s_resources && var.iam_config.enabled && var.iam_config.enable_lb_controller_role ? 1 : 0

  metadata {
    name      = var.iam_config.lb_controller_service_account_name
    namespace = var.iam_config.lb_controller_service_account_namespace
    annotations = {
      "eks.amazonaws.com/role-arn" = module.iam[0].lb_controller_role_arn
    }
  }

  depends_on = [
    module.eks,
    module.iam,
    aws_eks_access_policy_association.terraform_admin
  ]
}

resource "kubernetes_service_account_v1" "cluster_autoscaler" {
  count = var.eks_config.enabled && var.enable_k8s_resources && var.iam_config.enabled && var.iam_config.enable_autoscaler_role ? 1 : 0

  metadata {
    name      = var.iam_config.autoscaler_service_account_name
    namespace = var.iam_config.autoscaler_service_account_namespace
    annotations = {
      "eks.amazonaws.com/role-arn" = module.iam[0].cluster_autoscaler_role_arn
    }
  }

  depends_on = [
    module.eks,
    module.iam,
    aws_eks_access_policy_association.terraform_admin
  ]
}

resource "kubernetes_service_account_v1" "external_secrets" {
  count = var.eks_config.enabled && var.enable_k8s_resources && var.iam_config.enabled && var.iam_config.enable_eso_role ? 1 : 0

  metadata {
    name      = var.iam_config.eso_service_account_name
    namespace = var.iam_config.eso_service_account_namespace
    annotations = {
      "eks.amazonaws.com/role-arn" = module.iam[0].eso_role_arn
    }
  }

  depends_on = [
    module.eks,
    module.iam,
    aws_eks_access_policy_association.terraform_admin
  ]
}

provider "helm" {
  kubernetes {
    host                   = module.eks[0].cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks[0].cluster_ca)
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      args        = ["eks", "get-token", "--cluster-name", module.eks[0].cluster_name, "--region", var.aws_region]
      command     = "aws"
    }
  }
}

module "kubernetes_addons" {
  source = "../../modules/kubernetes_addons"
  count  = var.eks_config.enabled && var.enable_k8s_resources && var.apply_kubernetes_addons ? 1 : 0

  path_to_app_manifests = "${path.module}/../../gitops/argocd/apps/dev"
  argocd_values         = file("${path.module}/../../gitops/helm/argocd/values/dev.yaml")

  # AWS Load Balancer Controller specific inputs
  vpc_id       = module.vpc.vpc_id
  cluster_name = local.cluster_name_effective
  aws_region   = var.aws_region

  tags = local.common_tags

  depends_on = [
    module.eks,
    kubernetes_service_account_v1.aws_load_balancer_controller,
    aws_eks_access_policy_association.terraform_admin
  ]
}

# Trust store for workload secret synchronization via ESO
resource "kubernetes_manifest" "cluster_secret_store" {
  count = var.eks_config.enabled && var.enable_k8s_resources && var.iam_config.enabled && var.iam_config.enable_eso_role ? 1 : 0

  manifest = {
    apiVersion = "external-secrets.io/v1beta1"
    kind       = "ClusterSecretStore"
    metadata = {
      name = "aws-secretsmanager"
    }
    spec = {
      provider = {
        aws = {
          service = "SecretsManager"
          region  = var.aws_region
          auth = {
            jwt = {
              serviceAccountRef = {
                name      = var.iam_config.eso_service_account_name
                namespace = var.iam_config.eso_service_account_namespace
              }
            }
          }
        }
      }
    }
  }

  depends_on = [
    kubernetes_service_account_v1.external_secrets,
    module.kubernetes_addons # Ensure ESO CRDs are present
  ]
}

################################################################################
# Platform Catalogs: ECR & Secrets
################################################################################

module "ecr_repositories" {
  source   = "../../modules/aws_ecr"
  for_each = var.ecr_repositories

  name     = each.key
  metadata = each.value.metadata
}

module "app_secrets" {
  source   = "../../modules/aws_secrets_manager"
  for_each = var.app_secrets

  name        = each.key
  description = each.value.description
  tags        = local.common_tags

  read_principals        = each.value.read_principals
  write_principals       = each.value.write_principals
  break_glass_principals = each.value.break_glass_principals

  metadata = each.value.metadata
}
