variable "cluster_name" {
  type        = string
  description = "Name of the EKS cluster."
}

variable "kubernetes_version" {
  type        = string
  description = "EKS Kubernetes version."
}

variable "vpc_id" {
  type        = string
  description = "VPC ID where the cluster will be deployed."
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnets used for the EKS cluster and node group."
}

variable "node_group_config" {
  description = "Configuration for the managed node group."
  type = object({
    name           = string
    min_size       = number
    max_size       = number
    desired_size   = number
    instance_types = list(string)
    disk_size      = number
    capacity_type  = string
    update_config = optional(object({
      max_unavailable            = optional(number)
      max_unavailable_percentage = optional(number)
    }))
  })
}

variable "tags" {
  type        = map(string)
  description = "Tags applied to EKS resources."
  default     = {}
}

variable "environment" {
  type        = string
  description = "Environment name for tagging."
  default     = ""
}

variable "access_config" {
  description = "EKS access configuration for the cluster."
  type = object({
    authentication_mode                         = string
    bootstrap_cluster_creator_admin_permissions = bool
  })
  default = {
    authentication_mode                         = "API_AND_CONFIG_MAP"
    bootstrap_cluster_creator_admin_permissions = true
  }
}

variable "enable_ssh_break_glass" {
  type        = bool
  description = "Whether to enable SSH break-glass access to worker nodes."
  default     = false
}

variable "ssh_key_name" {
  type        = string
  description = "EC2 key pair name for SSH break-glass access."
  default     = null
}

variable "ssh_source_security_group_ids" {
  type        = list(string)
  description = "Security group IDs allowed to SSH into worker nodes."
  default     = []
}

variable "addon_versions" {
  description = "Optional map of EKS addon versions to pin by addon name."
  type        = map(string)
  default     = {}
}

variable "addon_replica_counts" {
  description = "Optional map of addon replica counts by addon name."
  type        = map(number)
  default     = {}
}

variable "enable_storage_addons" {
  description = "Whether to install storage-related EKS managed add-ons (EBS, EFS, snapshot)."
  type        = bool
  default     = true
}
