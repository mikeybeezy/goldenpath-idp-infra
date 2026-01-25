# AGENT_CONTEXT: Read .agent/README.md for rules
################################################################################
# Platform RDS Outputs
#
# NOTE: Apps should NOT reference these outputs directly.
# They should use AWS Secrets Manager via ExternalSecrets.
# These outputs are for documentation and debugging only.
################################################################################

################################################################################
# RDS Instance
################################################################################

output "db_instance_identifier" {
  description = "The RDS instance identifier"
  value       = aws_db_instance.platform.identifier
}

output "db_instance_endpoint" {
  description = "The connection endpoint (for documentation only - apps use Secrets Manager)"
  value       = aws_db_instance.platform.endpoint
}

output "db_instance_address" {
  description = "The hostname of the RDS instance"
  value       = aws_db_instance.platform.address
}

output "db_instance_port" {
  description = "The database port"
  value       = aws_db_instance.platform.port
}

output "db_instance_arn" {
  description = "The ARN of the RDS instance"
  value       = aws_db_instance.platform.arn
}

################################################################################
# Network
################################################################################

output "db_subnet_group_name" {
  description = "The DB subnet group name"
  value       = aws_db_subnet_group.platform.name
}

output "security_group_id" {
  description = "The security group ID for the RDS instance"
  value       = aws_security_group.rds.id
}

output "vpc_id" {
  description = "The VPC ID where RDS is deployed"
  value       = data.aws_vpc.platform.id
}

################################################################################
# Secrets
################################################################################

output "master_secret_arn" {
  description = "The ARN of the master credentials secret"
  value       = aws_secretsmanager_secret.master.arn
}

output "master_secret_name" {
  description = "The name of the master credentials secret"
  value       = aws_secretsmanager_secret.master.name
}

output "app_secret_arns" {
  description = "Map of application secret ARNs"
  value       = { for k, v in aws_secretsmanager_secret.app : k => v.arn }
}

output "app_secret_names" {
  description = "Map of application secret names"
  value       = { for k, v in aws_secretsmanager_secret.app : k => v.name }
}

################################################################################
# Rotation
# V1: Manual rotation enforced via CI workflows
# V1.1: Will add rotation_lambda_arn and rotation_lambda_name outputs
################################################################################

output "rotation_policy" {
  description = "Secret rotation policy for this environment"
  value = {
    rotation_days      = var.rotation_days
    enforcement_method = "ci-workflow"
    workflow           = ".github/workflows/secret-rotation-check.yml"
  }
}

################################################################################
# Monitoring
################################################################################

output "cloudwatch_alarm_arns" {
  description = "Map of CloudWatch alarm ARNs"
  value = {
    cpu_warning           = aws_cloudwatch_metric_alarm.cpu_warning.arn
    cpu_critical          = aws_cloudwatch_metric_alarm.cpu_critical.arn
    memory_warning        = aws_cloudwatch_metric_alarm.memory_warning.arn
    memory_critical       = aws_cloudwatch_metric_alarm.memory_critical.arn
    storage_warning       = aws_cloudwatch_metric_alarm.storage_warning.arn
    storage_critical      = aws_cloudwatch_metric_alarm.storage_critical.arn
    connections_warning   = aws_cloudwatch_metric_alarm.connections_warning.arn
    read_latency_warning  = aws_cloudwatch_metric_alarm.read_latency_warning.arn
    write_latency_warning = aws_cloudwatch_metric_alarm.write_latency_warning.arn
  }
}
