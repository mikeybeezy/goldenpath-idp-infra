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
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = ">= 1.14.0"
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

  # ADR-0179: Dynamic hostname generation for ephemeral clusters
  # Persistent: {env}.goldenpathidp.io (e.g., dev.goldenpathidp.io)
  # Ephemeral:  b-{buildId}.{env}.goldenpathidp.io (e.g., b-23-01-26-01.dev.goldenpathidp.io)
  base_domain = var.route53_config.enabled ? var.route53_config.domain_name : "goldenpathidp.io"
  host_suffix = local.cluster_lifecycle == "ephemeral" && local.build_id != "" ? (
    "b-${local.build_id}.${local.environment}.${local.base_domain}"
  ) : "${local.environment}.${local.base_domain}"

  # ADR-0178: DNS ownership ID for ExternalDNS txt records
  # Persistent: goldenpath-{env}
  # Ephemeral:  goldenpath-{env}-{buildId}
  dns_owner_id = local.cluster_lifecycle == "ephemeral" && local.build_id != "" ? (
    "goldenpath-${local.environment}-${local.build_id}"
  ) : "goldenpath-${local.environment}"

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
# IMPORTANT: This guard FAILS CLOSED - if we cannot verify the build_id is unique,
# we block the build to prevent state collisions. See ADR-0155.
data "external" "build_id_check" {
  count = var.cluster_lifecycle == "ephemeral" && var.build_id != "" ? 1 : 0
  program = ["bash", "-c", <<-EOT
    set -e
    BUILD_ID="${var.build_id}"
    ENV="${var.environment}"
    REGISTRY_BRANCH="${var.governance_registry_branch}"
    CSV_PATH="environments/development/latest/build_timings.csv"

    # Fetch latest CSV from governance-registry branch
    CSV_CONTENT=$(git show "origin/$REGISTRY_BRANCH:$CSV_PATH" 2>/dev/null || echo "")

    # FAIL CLOSED: If we cannot read the registry, we cannot verify uniqueness.
    # Block the build rather than allowing potential state collisions.
    if [ -z "$CSV_CONTENT" ]; then
      echo '{"exists":"unknown","registry_available":"false","error":"Cannot verify build_id uniqueness - governance-registry branch not available. Run: git fetch origin governance-registry"}'
      exit 0
    fi

    # Check if build_id exists for this environment (skip header)
    if echo "$CSV_CONTENT" | grep -q ",$ENV,$BUILD_ID," 2>/dev/null; then
      echo '{"exists":"true","registry_available":"true","build_id":"'"$BUILD_ID"'","environment":"'"$ENV"'"}'
    else
      echo '{"exists":"false","registry_available":"true","build_id":"'"$BUILD_ID"'","environment":"'"$ENV"'"}'
    fi
  EOT
  ]
}

# Enforce build_id immutability via lifecycle precondition
resource "null_resource" "enforce_build_id_immutability" {
  count = var.cluster_lifecycle == "ephemeral" && var.build_id != "" ? 1 : 0

  lifecycle {
    # PRECONDITION 1: Governance registry must be available (fail-closed guard)
    precondition {
      condition     = var.allow_build_id_reuse || try(data.external.build_id_check[0].result.registry_available, "false") == "true"
      error_message = <<-EOT
        Cannot verify build_id uniqueness - governance-registry branch not available.

        The build_id immutability guard requires access to the governance-registry branch
        to verify that ${var.build_id} has not been previously used. Without this check,
        we cannot guarantee state isolation and must block the build (fail-closed).

        To fix this, run:
          git fetch origin governance-registry

        Then retry your terraform apply command.

        If you are running in CI, ensure the workflow fetches the governance-registry branch:
          - uses: actions/checkout@v4
            with:
              fetch-depth: 0
          - run: git fetch origin governance-registry

        To bypass this check (NOT recommended):
          terraform apply -var="allow_build_id_reuse=true"
      EOT
    }

    # PRECONDITION 2: Build ID must not already exist
    precondition {
      condition     = var.allow_build_id_reuse || try(data.external.build_id_check[0].result.exists, "true") == "false"
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

################################################################################
# IAM Module - IRSA Roles Only
# NOTE: EKS cluster and node group roles are created by the EKS module.
# This module only manages IRSA roles (autoscaler, lb-controller, eso).
# See: session_capture/2026-01-20-persistent-cluster-deployment.md
################################################################################
module "iam" {
  source = "../../modules/aws_iam"
  count  = var.iam_config.enabled ? 1 : 0

  # OIDC provider for IRSA
  oidc_role_name    = "${var.iam_config.oidc_role_name != "" ? var.iam_config.oidc_role_name : "${local.base_name_prefix}-eks-oidc-role"}${local.role_suffix}"
  oidc_issuer_url   = module.eks[0].oidc_issuer_url
  oidc_provider_arn = module.eks[0].oidc_provider_arn
  oidc_audience     = var.iam_config.oidc_audience
  oidc_subject      = var.iam_config.oidc_subject

  # Cluster Autoscaler IRSA
  enable_autoscaler_role               = var.iam_config.enable_autoscaler_role
  autoscaler_role_name                 = "${var.iam_config.autoscaler_role_name}${local.role_suffix}"
  autoscaler_policy_arn                = var.iam_config.autoscaler_policy_arn
  autoscaler_service_account_namespace = var.iam_config.autoscaler_service_account_namespace
  autoscaler_service_account_name      = var.iam_config.autoscaler_service_account_name

  # AWS Load Balancer Controller IRSA
  enable_lb_controller_role               = var.iam_config.enable_lb_controller_role
  lb_controller_role_name                 = "${var.iam_config.lb_controller_role_name}${local.role_suffix}"
  lb_controller_policy_arn                = var.iam_config.lb_controller_policy_arn
  lb_controller_service_account_namespace = var.iam_config.lb_controller_service_account_namespace
  lb_controller_service_account_name      = var.iam_config.lb_controller_service_account_name

  # External Secrets Operator IRSA
  enable_eso_role               = var.iam_config.enable_eso_role
  eso_role_name                 = "${var.iam_config.eso_role_name}${local.role_suffix}"
  eso_service_account_namespace = var.iam_config.eso_service_account_namespace
  eso_service_account_name      = var.iam_config.eso_service_account_name

  # ExternalDNS IRSA
  enable_external_dns_role               = var.iam_config.enable_external_dns_role
  external_dns_role_name                 = "${var.iam_config.external_dns_role_name}${local.role_suffix}"
  external_dns_policy_arn                = var.iam_config.external_dns_policy_arn
  external_dns_service_account_namespace = var.iam_config.external_dns_service_account_namespace
  external_dns_service_account_name      = var.iam_config.external_dns_service_account_name
  external_dns_zone_id                   = var.route53_config.zone_id

  # RDS Provisioner IRSA (ADR-0165)
  enable_rds_provisioner_role               = var.iam_config.enable_rds_provisioner_role
  rds_provisioner_role_name                 = "${var.iam_config.rds_provisioner_role_name}${local.role_suffix}"
  rds_provisioner_service_account_namespace = var.iam_config.rds_provisioner_service_account_namespace
  rds_provisioner_service_account_name      = var.iam_config.rds_provisioner_service_account_name

  environment = local.environment
  tags        = local.common_tags

  depends_on = [module.eks]
}

# Principal identity for bootstrapping admin access
data "aws_caller_identity" "current" {}

# Grant the Terraform runner (CI role or local user) admin access to the cluster
# NOTE: The cluster creator has admin access by default. Explicit creation causes ResourceInUseException.
# resource "aws_eks_access_entry" "terraform_admin" {
#   cluster_name  = module.eks[0].cluster_name
#   principal_arn = data.aws_caller_identity.current.arn
#   type          = "STANDARD"
#
#   tags = local.common_tags
#
#   depends_on = [module.eks]
# }

# resource "aws_eks_access_policy_association" "terraform_admin" {
#   cluster_name  = module.eks[0].cluster_name
#   principal_arn = aws_eks_access_entry.terraform_admin.principal_arn
#   policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
#
#   access_scope {
#     type = "cluster"
#   }
#
#   depends_on = [aws_eks_access_entry.terraform_admin]
# }

################################################################################
# Managed Kubernetes Resources (ESO / Add-ons)
################################################################################

# -----------------------------------------------------------------------------
# Data source to fetch EKS cluster info for provider configuration
# -----------------------------------------------------------------------------
# IMPORTANT: No depends_on here! Data sources must read directly from AWS so that
# providers can be configured immediately.
#
# The count condition includes enable_k8s_resources so that:
# - Pass 1 (enable_k8s_resources=false): Data source count=0, no AWS read attempted
# - Pass 2 (enable_k8s_resources=true): Data source count=1, reads existing cluster
#
# Bootstrap v4 creates EKS in Pass 1 without k8s resources, then Pass 2 enables
# them after the cluster exists. The try() fallbacks in locals provide dummy
# values when data sources have count=0.
# -----------------------------------------------------------------------------
data "aws_eks_cluster" "this" {
  count = var.eks_config.enabled && var.enable_k8s_resources ? 1 : 0
  name  = local.cluster_name_effective
}

data "aws_eks_cluster_auth" "this" {
  count = var.eks_config.enabled && var.enable_k8s_resources ? 1 : 0
  name  = local.cluster_name_effective
}

locals {
  # Provider configuration with fallbacks for bootstrap scenario
  # When EKS doesn't exist, use dummy values that will prevent provider errors
  # The resources using these providers have count=0 when enable_k8s_resources=false
  k8s_host    = try(data.aws_eks_cluster.this[0].endpoint, "https://localhost")
  k8s_ca_cert = try(base64decode(data.aws_eks_cluster.this[0].certificate_authority[0].data), "")
  k8s_token   = try(data.aws_eks_cluster_auth.this[0].token, "")
  k8s_cluster = try(data.aws_eks_cluster.this[0].name, "placeholder")
}

provider "kubernetes" {
  host                   = local.k8s_host
  cluster_ca_certificate = local.k8s_ca_cert
  token                  = local.k8s_token
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

  ]
}

resource "kubernetes_namespace_v1" "external_secrets" {
  count = var.eks_config.enabled && var.enable_k8s_resources && var.iam_config.enabled && var.iam_config.enable_eso_role ? 1 : 0

  metadata {
    name = var.iam_config.eso_service_account_namespace
  }
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
    kubernetes_namespace_v1.external_secrets
  ]
}

resource "kubernetes_service_account_v1" "external_dns" {
  count = var.eks_config.enabled && var.enable_k8s_resources && var.iam_config.enabled && var.iam_config.enable_external_dns_role ? 1 : 0

  metadata {
    name      = var.iam_config.external_dns_service_account_name
    namespace = var.iam_config.external_dns_service_account_namespace
    annotations = {
      "eks.amazonaws.com/role-arn" = module.iam[0].external_dns_role_arn
    }
  }

  depends_on = [
    module.eks,
    module.iam,
  ]
}

provider "kubectl" {
  host                   = local.k8s_host
  cluster_ca_certificate = local.k8s_ca_cert
  token                  = local.k8s_token
  load_config_file       = false
}

provider "helm" {
  kubernetes {
    host                   = local.k8s_host
    cluster_ca_certificate = local.k8s_ca_cert
    token                  = local.k8s_token
  }
}

resource "kubernetes_ingress_class_v1" "kong" {
  count = var.eks_config.enabled && var.enable_k8s_resources && var.apply_kubernetes_addons ? 1 : 0

  metadata {
    name = "kong"
  }

  spec {
    controller = "ingress-controllers.konghq.com/kong"
  }

  depends_on = [module.eks]
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

  # ADR-0178, ADR-0179: Bootstrap values for dynamic hostname generation
  bootstrap_values = {
    host_suffix  = local.host_suffix
    dns_owner_id = local.dns_owner_id
    lifecycle    = local.cluster_lifecycle
    build_id     = local.build_id
    max_tier     = local.cluster_lifecycle == "ephemeral" ? "1.5" : "3"
  }

  tags = local.common_tags

  depends_on = [
    module.eks,
    kubernetes_service_account_v1.aws_load_balancer_controller,
    kubernetes_service_account_v1.external_dns,
    kubernetes_ingress_class_v1.kong,
    kubernetes_namespace_v1.argocd
  ]
}

################################################################################
# ArgoCD Namespace (Prerequisite for ArgoCD Bootstrap ConfigMap)
################################################################################
#
# Creates the argocd namespace BEFORE the bootstrap ConfigMap or ArgoCD Helm
# installation. This prevents "namespace not found" errors during v4 bootstrap.
#
# Root Cause Prevention: ArgoCD is installed via Helm AFTER Terraform, but the
# bootstrap ConfigMap needs the namespace to exist during Terraform's apply.
# Without this, every fresh cluster build fails with "namespaces argocd not found".
#
# See: session_capture/2026-01-24-persistent-cluster-teardown-and-deploy-fix.md
################################################################################

resource "kubernetes_namespace_v1" "argocd" {
  count = var.eks_config.enabled && var.enable_k8s_resources ? 1 : 0

  metadata {
    name = "argocd"
    labels = {
      "app.kubernetes.io/part-of" = "goldenpath-idp"
      "goldenpath.idp/managed-by" = "terraform"
      "goldenpath.idp/component"  = "gitops"
    }
  }
}

################################################################################
# Platform System Namespace (ADR-0165 - RDS Provisioning Execution)
################################################################################
#
# Creates the platform-system namespace for platform automation workloads.
# Primary use case: K8s Jobs for RDS user/database provisioning that require
# VPC access to reach private RDS endpoints.
#
# This namespace is created by Terraform (not ArgoCD) to ensure it exists
# BEFORE RDS provisioning runs - avoiding chicken-and-egg dependency.
#
# See: ADR-0165-rds-user-db-provisioning-automation.md
################################################################################

resource "kubernetes_namespace_v1" "platform_system" {
  count = var.eks_config.enabled && var.enable_k8s_resources ? 1 : 0

  metadata {
    name = "platform-system"
    labels = {
      "app.kubernetes.io/part-of" = "goldenpath-platform"
      "goldenpath.idp/managed-by" = "terraform"
      "goldenpath.idp/component"  = "platform-automation"
    }
  }
}

resource "kubernetes_service_account_v1" "platform_provisioner" {
  count = var.eks_config.enabled && var.enable_k8s_resources && var.iam_config.enabled ? 1 : 0

  metadata {
    name      = "platform-provisioner"
    namespace = kubernetes_namespace_v1.platform_system[0].metadata[0].name
    annotations = {
      "eks.amazonaws.com/role-arn" = module.iam[0].rds_provisioner_role_arn
    }
    labels = {
      "app.kubernetes.io/part-of" = "goldenpath-platform"
      "goldenpath.idp/managed-by" = "terraform"
    }
  }

  depends_on = [
    module.eks,
    module.iam,
    kubernetes_namespace_v1.platform_system
  ]
}

################################################################################
# ArgoCD Bootstrap ConfigMap (ADR-0178, ADR-0179, ADR-0180)
################################################################################
#
# This ConfigMap provides bootstrap values for ArgoCD app-of-apps to configure
# platform applications. Values are computed by Terraform and consumed by Helm.
#
# See: IMPL-0001-tiered-bootstrap-and-hostname-generation.md Phase 4
################################################################################

resource "kubernetes_config_map_v1" "argocd_bootstrap" {
  count = var.eks_config.enabled && var.enable_k8s_resources ? 1 : 0

  metadata {
    name      = "argocd-bootstrap-config"
    namespace = kubernetes_namespace_v1.argocd[0].metadata[0].name
    labels = {
      "app.kubernetes.io/part-of"  = "goldenpath-idp"
      "goldenpath.idp/managed-by"  = "terraform"
      "goldenpath.idp/config-type" = "bootstrap"
    }
  }

  data = {
    # Bootstrap mode and build identification
    "bootstrap.mode"    = var.cluster_lifecycle
    "bootstrap.buildId" = var.build_id
    "bootstrap.maxTier" = var.cluster_lifecycle == "ephemeral" ? "1.5" : "3"

    # DNS configuration (ADR-0179)
    "dns.hostSuffix" = local.host_suffix
    "dns.ownerId"    = local.dns_owner_id
    "dns.baseDomain" = local.base_domain

    # Platform availability flags (ADR-0178)
    "platform.rdsAvailable" = tostring(var.rds_config.enabled && var.cluster_lifecycle == "persistent")
    "platform.rdsEndpoint"  = var.rds_config.enabled && var.cluster_lifecycle == "persistent" ? module.platform_rds[0].db_instance_address : ""

    # Environment metadata
    "environment.name"   = local.environment
    "environment.region" = var.aws_region
    "cluster.name"       = local.cluster_name_effective
  }

  depends_on = [
    module.eks,
    kubernetes_namespace_v1.argocd
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

  # Enable adopt-or-create pattern for idempotent deploys
  # When state is lost, this allows re-deploy without manual intervention
  adopt_existing = true

  # Explicitly set create_policy to avoid "count depends on computed values" error
  # when read_principals contains module.iam[0].eso_role_arn (computed at apply time)
  create_policy = length(each.value.read_principals) > 0 || length(each.value.write_principals) > 0 || length(each.value.break_glass_principals) > 0 || var.iam_config.enabled

  # Dynamically append the ESO role (if IAM is enabled) to ensure correct ordering and ARN logic
  read_principals = var.iam_config.enabled ? distinct(concat(each.value.read_principals, [module.iam[0].eso_role_arn])) : each.value.read_principals

  write_principals       = each.value.write_principals
  break_glass_principals = each.value.break_glass_principals

  metadata      = each.value.metadata
  initial_value = each.value.initial_value
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

################################################################################
# Platform RDS: Two Deployment Models (ADR-0160)
################################################################################
#
# Option A: Standalone Bounded Context (ADR-0158)
#   - Directory: envs/dev-rds/
#   - Command: make rds-apply ENV=dev (separate from EKS)
#   - Use case: Team-requested persistence, Backstage self-service
#
# Option B: Coupled with EKS (below) - PERSISTENT MODE ONLY
#   - Toggle: rds_config.enabled = true in terraform.tfvars
#   - Requires: cluster_lifecycle = "persistent"
#   - Command: make apply ENV=dev (single command)
#   - Use case: Simple deployment with full teardown support
#
# IMPORTANT: Coupled RDS is BLOCKED in ephemeral mode to prevent orphaned resources.
# See: docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md
################################################################################

# Fail-fast guard: Block coupled RDS in ephemeral builds
# This check validates that RDS is not enabled when cluster_lifecycle is ephemeral
# The precondition must reference config values to satisfy Terraform's validation
resource "null_resource" "rds_ephemeral_guard" {
  count = var.rds_config.enabled && var.cluster_lifecycle == "ephemeral" ? 1 : 0

  lifecycle {
    precondition {
      # This condition is always false when count > 0, but references config values
      condition     = !(var.rds_config.enabled && var.cluster_lifecycle == "ephemeral")
      error_message = <<-EOT
        ERROR: Coupled RDS is not allowed in ephemeral EKS builds.

        When cluster_lifecycle = "ephemeral", RDS cannot be coupled because:
        - Ephemeral teardown does not capture RDS resources
        - This creates orphaned databases and state conflicts

        Options:
        1. Use persistent mode: Set cluster_lifecycle = "persistent" in terraform.tfvars
        2. Use standalone RDS: Set rds_config.enabled = false and run:
           make rds-apply ENV=${var.environment}

        See: docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md
      EOT
    }
  }
}

module "platform_rds" {
  source = "../../modules/aws_rds"
  # Only create when enabled AND in persistent mode (ephemeral blocked by guard above)
  count = var.rds_config.enabled && var.cluster_lifecycle == "persistent" ? 1 : 0

  identifier = "${local.base_name_prefix}-${var.rds_config.identifier}"
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.subnets.private_subnet_ids

  # Engine
  engine_version       = var.rds_config.engine_version
  engine_version_major = split(".", var.rds_config.engine_version)[0]
  instance_class       = var.rds_config.instance_class

  # Storage
  allocated_storage     = var.rds_config.allocated_storage
  max_allocated_storage = var.rds_config.max_allocated_storage

  # High Availability
  multi_az = var.rds_config.multi_az

  # Backup & Lifecycle
  backup_retention_period = var.rds_config.backup_retention_days
  deletion_protection     = var.rds_config.deletion_protection
  skip_final_snapshot     = var.rds_config.skip_final_snapshot

  # Network - allow from VPC CIDR
  allowed_cidr_blocks = [var.vpc_cidr]

  # Secrets - build_id scoped paths for ephemeral (bounded context isolation)
  # Persistent: goldenpath/dev/rds/master
  # Ephemeral:  goldenpath/dev/builds/20-01-26-01/rds/master
  create_master_secret = true
  master_secret_name = var.cluster_lifecycle == "ephemeral" ? (
    "goldenpath/${local.environment}/builds/${local.build_id}/rds/master"
    ) : (
    "goldenpath/${local.environment}/rds/master"
  )
  # 0-day recovery for ephemeral (immediate deletion), 7-day for persistent
  secret_recovery_window_in_days = var.cluster_lifecycle == "ephemeral" ? 0 : 7

  # Application databases with secrets - build_id scoped for ephemeral
  application_databases = {
    for k, v in var.rds_config.application_databases : k => {
      database_name = v.database_name
      username      = v.username
      secret_name = var.cluster_lifecycle == "ephemeral" ? (
        "goldenpath/${local.environment}/builds/${local.build_id}/${k}/postgres"
        ) : (
        "goldenpath/${local.environment}/${k}/postgres"
      )
    }
  }

  # Force SSL
  db_parameters = [
    {
      name  = "rds.force_ssl"
      value = "1"
    },
    {
      name  = "log_min_duration_statement"
      value = "1000"
    }
  ]

  # Tags include ClusterName for teardown discovery in persistent mode
  tags = merge(
    local.common_tags,
    {
      ClusterName = local.cluster_name_effective
      Component   = "platform-rds-coupled"
    }
  )

  depends_on = [module.vpc, module.subnets]
}

################################################################################
# Route53 DNS Management
################################################################################
#
# Manages the goldenpathidp.io domain DNS records.
# The hosted zone was created manually and should be imported:
#   terraform import 'module.route53[0].aws_route53_zone.main[0]' Z0032802NEMSL43VHH4E
#
# Or set create_hosted_zone = false to use the existing zone via data source.
#
# ExternalDNS (deployed via ArgoCD) will manage dynamic DNS records for
# services with the external-dns.alpha.kubernetes.io/hostname annotation.
################################################################################

# Data source to get Kong LoadBalancer hostname for wildcard CNAME
data "kubernetes_service_v1" "kong_proxy" {
  count = var.route53_config.enabled && var.eks_config.enabled && var.enable_k8s_resources ? 1 : 0

  metadata {
    name      = var.route53_config.kong_service_name
    namespace = var.route53_config.kong_service_namespace
  }

  depends_on = [module.kubernetes_addons]
}

locals {
  # Kong LoadBalancer hostname (e.g., k8s-kongsyst-devkongk-xxx.elb.eu-west-2.amazonaws.com)
  kong_lb_hostname = try(
    data.kubernetes_service_v1.kong_proxy[0].status[0].load_balancer[0].ingress[0].hostname,
    ""
  )
}

module "route53" {
  source = "../../modules/aws_route53"
  count  = var.route53_config.enabled ? 1 : 0

  domain_name        = var.route53_config.domain_name
  zone_id            = var.route53_config.zone_id
  environment        = local.environment
  create_hosted_zone = var.route53_config.create_hosted_zone
  zone_comment       = "Golden Path IDP - ${local.environment} environment"

  # Wildcard CNAME for *.dev.goldenpathidp.io -> Kong LoadBalancer
  create_wildcard_record = var.route53_config.create_wildcard_record
  wildcard_target        = local.kong_lb_hostname

  record_ttl    = var.route53_config.record_ttl
  cname_records = var.route53_config.cname_records

  tags = local.common_tags

  depends_on = [module.kubernetes_addons]
}
