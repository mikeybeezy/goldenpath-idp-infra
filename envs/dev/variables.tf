variable "environment" {
  type        = string
  description = "Environment identifier (dev/test/staging/prod)."
}

variable "name_prefix" {
  type        = string
  description = "Prefix applied to resource names."
  default     = ""
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC."
}

variable "public_subnets" {
  description = "List of public subnet definitions."
  type = list(object({
    name              = string
    cidr_block        = string
    availability_zone = string
    tags              = optional(map(string))
  }))
}

variable "private_subnets" {
  description = "List of private subnet definitions."
  type = list(object({
    name              = string
    cidr_block        = string
    availability_zone = string
    tags              = optional(map(string))
  }))
}

variable "common_tags" {
  type        = map(string)
  description = "Additional tags applied to resources."
  default     = {}
}

variable "compute_config" {
  description = "Configuration for the optional EC2 instance."
  type = object({
    enabled                       = bool
    name                          = string
    ami_id                        = string
    instance_type                 = string
    subnet_type                   = string
    additional_security_group_ids = list(string)
    ssh_key_name                  = string
    user_data                     = string
    iam_instance_profile          = string
    network_interface_description = string
    root_volume_size              = number
    root_volume_type              = string
    root_volume_encrypted         = bool
  })
  default = {
    enabled                       = false
    name                          = ""
    ami_id                        = ""
    instance_type                 = "t3.micro"
    subnet_type                   = "private"
    additional_security_group_ids = []
    ssh_key_name                  = null
    user_data                     = null
    iam_instance_profile          = null
    network_interface_description = "Managed by Terraform"
    root_volume_size              = 20
    root_volume_type              = "gp3"
    root_volume_encrypted         = true
  }
}

variable "iam_config" {
  description = "Configuration for optional EKS IAM roles and OIDC assume role."
  type = object({
    enabled             = bool
    cluster_role_name   = string
    node_group_role_name = string
    oidc_role_name      = string
    oidc_issuer_url     = string
    oidc_provider_arn   = string
    oidc_audience       = string
    oidc_subject        = string
  })
  default = {
    enabled              = false
    cluster_role_name    = ""
    node_group_role_name = ""
    oidc_role_name       = ""
    oidc_issuer_url      = ""
    oidc_provider_arn    = ""
    oidc_audience        = "sts.amazonaws.com"
    oidc_subject         = ""
  }
}

variable "eks_config" {
  description = "Configuration for the optional EKS cluster."
  type = object({
    enabled      = bool
    cluster_name = string
    version      = string
    node_group = object({
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
  })
  default = {
    enabled      = false
    cluster_name = ""
    version      = "1.29"
    node_group = {
      name           = "default"
      min_size       = 1
      max_size       = 1
      desired_size   = 1
      instance_types = ["t3.medium"]
      disk_size      = 20
      capacity_type  = "ON_DEMAND"
      update_config = {
        max_unavailable = 1
      }
    }
  }
}
