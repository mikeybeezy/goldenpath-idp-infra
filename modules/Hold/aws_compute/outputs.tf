output "instance_id" {
  description = "ID of the EC2 instance."
  value       = aws_instance.app.id
}

output "private_ip" {
  description = "Private IP address of the EC2 instance."
  value       = aws_instance.app.private_ip
}

output "network_interface_id" {
  description = "ID of the network interface attached to the instance."
  value       = aws_network_interface.instance.id
}
