output "vpc_id" {
  description = "ID of the created VPC."
  value       = aws_vpc.main.id
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway associated with the VPC (if any)."
  value       = local.internet_gateway_id
}

output "public_route_table_id" {
  description = "ID of the created public route table (if enabled)."
  value       = try(aws_route_table.public[0].id, null)
}
