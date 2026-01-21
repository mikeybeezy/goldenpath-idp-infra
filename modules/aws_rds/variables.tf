################################################################################
# RDS Module Variables
################################################################################

# -----------------------------------------------------------------------------
# Required Variables
# -----------------------------------------------------------------------------

variable "identifier" {
  description = "The name/identifier for the RDS instance"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where RDS will be deployed"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the DB subnet group"
  type        = list(string)
}

# -----------------------------------------------------------------------------
# Component Creation Toggles
# -----------------------------------------------------------------------------

variable "create_subnet_group" {
  description = "Whether to create a new DB subnet group"
  type        = bool
  default     = true
}

variable "create_security_group" {
  description = "Whether to create a new security group"
  type        = bool
  default     = true
}

variable "create_parameter_group" {
  description = "Whether to create a new parameter group"
  type        = bool
  default     = true
}

variable "create_random_password" {
  description = "Whether to generate a random master password"
  type        = bool
  default     = true
}

# -----------------------------------------------------------------------------
# Existing Resource References (when not creating new)
# -----------------------------------------------------------------------------

variable "existing_subnet_group_name" {
  description = "Name of existing DB subnet group to use (when create_subnet_group = false)"
  type        = string
  default     = null
}

variable "existing_security_group_ids" {
  description = "List of existing security group IDs to use (when create_security_group = false)"
  type        = list(string)
  default     = []
}

variable "existing_parameter_group_name" {
  description = "Name of existing parameter group to use (when create_parameter_group = false)"
  type        = string
  default     = null
}

# -----------------------------------------------------------------------------
# Network & Security
# -----------------------------------------------------------------------------

variable "allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access the RDS instance"
  type        = list(string)
  default     = []
}

variable "allowed_security_group_ids" {
  description = "List of security group IDs allowed to access the RDS instance"
  type        = list(string)
  default     = []
}

# -----------------------------------------------------------------------------
# Engine Configuration
# -----------------------------------------------------------------------------

variable "engine_version" {
  description = "PostgreSQL engine version (e.g., 15.4)"
  type        = string
  default     = "15.4"
}

variable "engine_version_major" {
  description = "PostgreSQL major version for parameter group family (e.g., 15)"
  type        = string
  default     = "15"
}

variable "instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

# -----------------------------------------------------------------------------
# Storage Configuration
# -----------------------------------------------------------------------------

variable "allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Maximum storage for autoscaling in GB (0 to disable)"
  type        = number
  default     = 100
}

variable "storage_type" {
  description = "Storage type (gp2, gp3, io1)"
  type        = string
  default     = "gp3"
}

variable "storage_encrypted" {
  description = "Enable storage encryption"
  type        = bool
  default     = true
}

variable "kms_key_id" {
  description = "KMS key ID for storage encryption"
  type        = string
  default     = null
}

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------

variable "database_name" {
  description = "Name of the default database to create"
  type        = string
  default     = "platform"
}

variable "master_username" {
  description = "Master username for the RDS instance"
  type        = string
  default     = "postgres"
}

variable "master_password" {
  description = "Master password (used when create_random_password = false)"
  type        = string
  default     = null
  sensitive   = true
}

variable "db_parameters" {
  description = "List of DB parameter objects to apply"
  type = list(object({
    name         = string
    value        = string
    apply_method = optional(string, "immediate")
  }))
  default = [
    {
      name  = "log_min_duration_statement"
      value = "1000"
    }
  ]
}

# -----------------------------------------------------------------------------
# High Availability
# -----------------------------------------------------------------------------

variable "multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = false
}

# -----------------------------------------------------------------------------
# Backup & Maintenance
# -----------------------------------------------------------------------------

variable "backup_retention_period" {
  description = "Backup retention period in days"
  type        = number
  default     = 7
}

variable "backup_window" {
  description = "Preferred backup window (UTC)"
  type        = string
  default     = "03:00-04:00"
}

variable "maintenance_window" {
  description = "Preferred maintenance window (UTC)"
  type        = string
  default     = "Mon:04:00-Mon:05:00"
}

variable "delete_automated_backups" {
  description = "Delete automated backups on instance deletion"
  type        = bool
  default     = true
}

variable "deletion_protection" {
  description = "Enable deletion protection"
  type        = bool
  default     = false
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot on deletion"
  type        = bool
  default     = true
}

# -----------------------------------------------------------------------------
# Monitoring
# -----------------------------------------------------------------------------

variable "performance_insights_enabled" {
  description = "Enable Performance Insights"
  type        = bool
  default     = false
}

variable "performance_insights_retention_period" {
  description = "Performance Insights retention period in days"
  type        = number
  default     = 7
}

variable "enabled_cloudwatch_logs_exports" {
  description = "List of log types to export to CloudWatch"
  type        = list(string)
  default     = ["postgresql", "upgrade"]
}

# -----------------------------------------------------------------------------
# Lifecycle
# -----------------------------------------------------------------------------

variable "apply_immediately" {
  description = "Apply changes immediately (vs. during maintenance window)"
  type        = bool
  default     = true
}

# -----------------------------------------------------------------------------
# Secrets Management
# -----------------------------------------------------------------------------

variable "create_master_secret" {
  description = "Whether to create a Secrets Manager secret for master credentials"
  type        = bool
  default     = true
}

variable "master_secret_name" {
  description = "Name for the master credentials secret in Secrets Manager"
  type        = string
  default     = null
}

variable "secret_recovery_window_in_days" {
  description = "Number of days to retain a deleted secret before permanent deletion. Use 0 for immediate deletion (recommended for ephemeral clusters)."
  type        = number
  default     = 0

  validation {
    condition     = var.secret_recovery_window_in_days >= 0 && var.secret_recovery_window_in_days <= 30
    error_message = "secret_recovery_window_in_days must be between 0 and 30."
  }
}

variable "application_databases" {
  description = "Map of application databases to create secrets for"
  type = map(object({
    database_name = string
    username      = string
    secret_name   = string
  }))
  default = {}
}

# -----------------------------------------------------------------------------
# Tags
# -----------------------------------------------------------------------------

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
