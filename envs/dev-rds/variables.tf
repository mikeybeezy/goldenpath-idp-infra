################################################################################
# Platform RDS Variables
# Standalone bounded context for persistent data layer
################################################################################

################################################################################
# Core Configuration
################################################################################

variable "environment" {
  type        = string
  description = "Environment identifier (dev/staging/prod)"
}

variable "aws_region" {
  type        = string
  description = "AWS region for RDS deployment. Region-agnostic - set per environment."
  # No default - must be explicitly set
}

variable "identifier_prefix" {
  type        = string
  description = "Prefix for RDS instance identifier"
  default     = "goldenpath-platform-db"
}

variable "owner_team" {
  type        = string
  description = "Owning team for audit tags"
  default     = "platform-team"
}

variable "cost_center" {
  type        = string
  description = "Cost center for billing allocation"
  default     = "platform"
}

################################################################################
# Database Engine
################################################################################

variable "engine_version" {
  type        = string
  description = "PostgreSQL engine version"
  default     = "15.4"
}

variable "engine_version_major" {
  type        = string
  description = "PostgreSQL major version for parameter group family"
  default     = "15"
}

variable "instance_class" {
  type        = string
  description = "RDS instance class"
  default     = "db.t3.micro"
}

################################################################################
# Storage
################################################################################

variable "allocated_storage" {
  type        = number
  description = "Initial allocated storage in GB"
  default     = 20
}

variable "max_allocated_storage" {
  type        = number
  description = "Maximum storage for autoscaling in GB"
  default     = 100
}

variable "kms_key_id" {
  type        = string
  description = "KMS key ARN for encryption. If null, uses default aws/rds key."
  default     = null
}

################################################################################
# Database Configuration
################################################################################

variable "database_name" {
  type        = string
  description = "Name of the default database"
  default     = "platform"
}

variable "master_username" {
  type        = string
  description = "Master username for the database"
  default     = "platformadmin"
}

################################################################################
# High Availability
################################################################################

variable "multi_az" {
  type        = bool
  description = "Enable Multi-AZ deployment for high availability"
  default     = false # Set true for prod
}

################################################################################
# Backup & Maintenance
################################################################################

variable "backup_retention_period" {
  type        = number
  description = "Number of days to retain automated backups"
  default     = 7 # 35 for prod
}

variable "backup_window" {
  type        = string
  description = "Daily time range for automated backups (UTC)"
  default     = "03:00-04:00"
}

variable "maintenance_window" {
  type        = string
  description = "Weekly time range for maintenance (UTC)"
  default     = "Mon:04:00-Mon:05:00"
}

variable "apply_immediately" {
  type        = bool
  description = "Apply changes immediately vs during maintenance window"
  default     = true # Set false for prod
}

################################################################################
# Monitoring
################################################################################

variable "performance_insights_retention_period" {
  type        = number
  description = "Retention period for Performance Insights data (days)"
  default     = 7 # Free tier is 7 days
}

variable "max_connections" {
  type        = number
  description = "Expected max connections (for alarm thresholds)"
  default     = 100 # db.t3.micro default
}

variable "alarm_sns_topic_arn" {
  type        = string
  description = "SNS topic ARN for CloudWatch alarm notifications"
  default     = ""
}

################################################################################
# Application Databases
################################################################################

variable "application_databases" {
  type = map(object({
    database_name = string
    username      = string
  }))
  description = "Map of application databases to create with their own credentials"
  default = {
    keycloak = {
      database_name = "keycloak"
      username      = "keycloak"
    }
    backstage = {
      database_name = "backstage"
      username      = "backstage"
    }
  }
}

################################################################################
# Secret Rotation
################################################################################

variable "rotation_days" {
  type        = number
  description = "Number of days between automatic secret rotations"
  default     = 30 # 14 for prod
}
