output "route_table_id" {
  description = "ID of the created route table."
  value       = aws_route_table.this.id
}

output "route_table_association_ids" {
  description = "IDs of the route table associations."
  value       = [for assoc in aws_route_table_association.this : assoc.id]
}
