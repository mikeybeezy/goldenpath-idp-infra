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
  })
}

variable "tags" {
  type        = map(string)
  description = "Tags applied to EKS resources."
  default     = {}
}
