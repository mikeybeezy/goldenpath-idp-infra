output "network_interface_id" {
  description = "ID of the created network interface."
  value       = aws_network_interface.this.id
}
