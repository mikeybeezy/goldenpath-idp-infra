################################################################################
# RDS Module Outputs
################################################################################

# -----------------------------------------------------------------------------
# RDS Instance
# -----------------------------------------------------------------------------

output "db_instance_id" {
  description = "The RDS instance ID"
  value       = aws_db_instance.this.id
}

output "db_instance_arn" {
  description = "The ARN of the RDS instance"
  value       = aws_db_instance.this.arn
}

output "db_instance_endpoint" {
  description = "The connection endpoint (host:port)"
  value       = aws_db_instance.this.endpoint
}

output "db_instance_address" {
  description = "The hostname of the RDS instance"
  value       = aws_db_instance.this.address
}

output "db_instance_port" {
  description = "The database port"
  value       = aws_db_instance.this.port
}

output "db_instance_name" {
  description = "The database name"
  value       = aws_db_instance.this.db_name
}

output "db_instance_username" {
  description = "The master username"
  value       = aws_db_instance.this.username
  sensitive   = true
}

output "db_instance_password" {
  description = "The master password"
  value       = local.master_password
  sensitive   = true
}

# -----------------------------------------------------------------------------
# Subnet Group
# -----------------------------------------------------------------------------

output "db_subnet_group_id" {
  description = "The DB subnet group ID"
  value       = try(aws_db_subnet_group.this[0].id, null)
}

output "db_subnet_group_name" {
  description = "The DB subnet group name"
  value       = local.subnet_group_name
}

# -----------------------------------------------------------------------------
# Security Group
# -----------------------------------------------------------------------------

output "security_group_id" {
  description = "The security group ID"
  value       = try(aws_security_group.this[0].id, null)
}

output "security_group_arn" {
  description = "The security group ARN"
  value       = try(aws_security_group.this[0].arn, null)
}

# -----------------------------------------------------------------------------
# Parameter Group
# -----------------------------------------------------------------------------

output "db_parameter_group_id" {
  description = "The DB parameter group ID"
  value       = try(aws_db_parameter_group.this[0].id, null)
}

output "db_parameter_group_name" {
  description = "The DB parameter group name"
  value       = local.parameter_group
}

# -----------------------------------------------------------------------------
# Secrets
# -----------------------------------------------------------------------------

output "master_secret_arn" {
  description = "The ARN of the master credentials secret"
  value       = try(aws_secretsmanager_secret.master[0].arn, null)
}

output "master_secret_name" {
  description = "The name of the master credentials secret"
  value       = try(aws_secretsmanager_secret.master[0].name, null)
}

output "app_secret_arns" {
  description = "Map of application secret ARNs"
  value       = { for k, v in aws_secretsmanager_secret.app : k => v.arn }
}

output "app_secret_names" {
  description = "Map of application secret names"
  value       = { for k, v in aws_secretsmanager_secret.app : k => v.name }
}
