output "eks_cluster_role_name" {
  description = "Name of the EKS cluster IAM role."
  value       = aws_iam_role.eks_cluster.name
}

output "eks_cluster_role_arn" {
  description = "ARN of the EKS cluster IAM role."
  value       = aws_iam_role.eks_cluster.arn
}

output "eks_node_group_role_name" {
  description = "Name of the EKS node group IAM role."
  value       = aws_iam_role.eks_node_group.name
}

output "eks_node_group_role_arn" {
  description = "ARN of the EKS node group IAM role."
  value       = aws_iam_role.eks_node_group.arn
}

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
