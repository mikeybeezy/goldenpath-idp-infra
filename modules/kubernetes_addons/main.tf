# Kubernetes Add-ons Module
# Orchestrates installation of ArgoCD, platform controllers, and bootstrap applications
#
# This module is split into logical components:
# - argocd.tf                  : ArgoCD GitOps controller
# - argocd_image_updater.tf    : ArgoCD Image Updater for automated image updates
# - aws_lb_controller.tf       : AWS Load Balancer Controller
# - metrics_server.tf          : Metrics Server for HPA and kubectl top
# - bootstrap_apps.tf          : Deploys all ArgoCD Application manifests
# - verification.tf            : Post-deployment validation checks
#
# Dependencies are managed via depends_on to ensure proper sequencing:
# 1. ArgoCD (base)
# 2. AWS LB Controller + Metrics Server (parallel)
# 3. ArgoCD Image Updater (after ArgoCD)
# 4. Bootstrap Apps (after all controllers)
# 5. Verification (after bootstrap apps)

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

# Data source to get current AWS account ID for ECR
data "aws_caller_identity" "current" {}

# Local values for reuse across components
locals {
  ecr_account_id = var.ecr_registry_id != "" ? var.ecr_registry_id : data.aws_caller_identity.current.account_id

  common_labels = {
    "app.kubernetes.io/managed-by" = "terraform"
    "goldenpath.idp/component"     = "platform-bootstrap"
  }
}
