################################################################################
# Environment Outputs
################################################################################

# -----------------------------------------------------------------------------
# EKS Cluster
# -----------------------------------------------------------------------------

output "cluster_name" {
  description = "The name of the EKS cluster"
  value       = var.eks_config.enabled ? module.eks[0].cluster_name : null
}

output "cluster_endpoint" {
  description = "The endpoint for the EKS cluster"
  value       = var.eks_config.enabled ? module.eks[0].cluster_endpoint : null
}

output "cluster_oidc_issuer_url" {
  description = "The OIDC issuer URL for the cluster"
  value       = var.eks_config.enabled ? module.eks[0].oidc_issuer_url : null
}

# -----------------------------------------------------------------------------
# VPC
# -----------------------------------------------------------------------------

output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = module.subnets.private_subnet_ids
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = module.subnets.public_subnet_ids
}

# -----------------------------------------------------------------------------
# Platform RDS (Coupled Option - when enabled AND persistent)
# Note: RDS is only created when rds_config.enabled AND cluster_lifecycle == "persistent"
# -----------------------------------------------------------------------------

output "rds_endpoint" {
  description = "The RDS instance endpoint (host:port)"
  value       = var.rds_config.enabled && var.cluster_lifecycle == "persistent" ? module.platform_rds[0].db_instance_endpoint : null
}

output "rds_address" {
  description = "The RDS instance hostname"
  value       = var.rds_config.enabled && var.cluster_lifecycle == "persistent" ? module.platform_rds[0].db_instance_address : null
}

output "rds_port" {
  description = "The RDS instance port"
  value       = var.rds_config.enabled && var.cluster_lifecycle == "persistent" ? module.platform_rds[0].db_instance_port : null
}

output "rds_master_secret_arn" {
  description = "ARN of the master credentials secret in Secrets Manager"
  value       = var.rds_config.enabled && var.cluster_lifecycle == "persistent" ? module.platform_rds[0].master_secret_arn : null
}

output "rds_app_secret_arns" {
  description = "Map of application database secret ARNs"
  value       = var.rds_config.enabled && var.cluster_lifecycle == "persistent" ? module.platform_rds[0].app_secret_arns : {}
}
