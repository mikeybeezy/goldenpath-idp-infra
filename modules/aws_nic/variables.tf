variable "name" {
  type        = string
  description = "Friendly name tag applied to the network interface."
}

variable "subnet_id" {
  type        = string
  description = "ID of the subnet where the network interface will reside."
}

variable "security_group_ids" {
  type        = list(string)
  description = "Security groups to associate with the network interface."
  default     = []
}

variable "private_ips" {
  type        = list(string)
  description = "Optional list of private IPs to assign. Leave empty for auto-assignment."
  default     = []
}

variable "description" {
  type        = string
  description = "Optional description for the network interface."
  default     = "Managed by Terraform"
}

variable "tags" {
  type        = map(string)
  description = "Additional tags to merge onto the network interface."
  default     = {}
}

variable "environment" {
  type        = string
  description = "Environment name for tagging."
  default     = ""
}
