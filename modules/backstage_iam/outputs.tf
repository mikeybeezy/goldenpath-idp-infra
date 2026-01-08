output "backstage_role_arn" {
  value       = aws_iam_role.backstage.arn
  description = "ARN of the IAM role for Backstage IRSA."
}

output "backstage_role_name" {
  value       = aws_iam_role.backstage.name
  description = "Name of the IAM role for Backstage IRSA."
}
