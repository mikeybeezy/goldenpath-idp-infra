################################################################################
# NOTE: eks_cluster_role and eks_node_group_role outputs removed.
# These roles are now created and output by the EKS module (modules/aws_eks).
# See: session_capture/2026-01-20-persistent-cluster-deployment.md
################################################################################

output "cluster_autoscaler_role_name" {
  description = "Name of the cluster autoscaler IAM role."
  value       = try(aws_iam_role.cluster_autoscaler[0].name, null)
}

output "cluster_autoscaler_role_arn" {
  description = "ARN of the cluster autoscaler IAM role."
  value       = try(aws_iam_role.cluster_autoscaler[0].arn, null)
}

output "lb_controller_role_name" {
  description = "Name of the AWS Load Balancer Controller IAM role."
  value       = try(aws_iam_role.lb_controller[0].name, null)
}

output "lb_controller_role_arn" {
  description = "ARN of the AWS Load Balancer Controller IAM role."
  value       = try(aws_iam_role.lb_controller[0].arn, null)
}

output "eso_role_name" {
  description = "Name of the External Secrets Operator IAM role."
  value       = try(aws_iam_role.eso[0].name, null)
}

output "eso_role_arn" {
  description = "ARN of the External Secrets Operator IAM role."
  value       = try(aws_iam_role.eso[0].arn, null)
}
