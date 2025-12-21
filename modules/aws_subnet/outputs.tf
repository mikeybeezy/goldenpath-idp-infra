output "public_subnet_ids" {
  description = "IDs of the created public subnets."
  value       = [for subnet in aws_subnet.public : subnet.id]
}

output "private_subnet_ids" {
  description = "IDs of the created private subnets."
  value       = [for subnet in aws_subnet.private : subnet.id]
}
