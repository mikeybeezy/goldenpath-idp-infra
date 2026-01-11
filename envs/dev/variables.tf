################################################################################
# Core Environment Metadata
################################################################################

variable "environment" {
  type        = string
  description = "Environment identifier (dev/test/staging/prod)."
}

variable "aws_region" {
  type        = string
  description = "AWS region for this environment."
  default     = "eu-west-2"
}

variable "name_prefix" {
  type        = string
  description = "Prefix applied to resource names."
  default     = ""
}

variable "owner_team" {
  type        = string
  description = "Owning team for audit tags."
  default     = "platform-team"
}

################################################################################
# Lifecycle & Ephemeral Settings
################################################################################

variable "cluster_lifecycle" {
  type        = string
  description = "Lifecycle for the environment: ephemeral or persistent."
  default     = "persistent"
  validation {
    condition     = contains(["ephemeral", "persistent"], var.cluster_lifecycle)
    error_message = "cluster_lifecycle must be one of: ephemeral, persistent."
  }
}

variable "build_id" {
  type        = string
  description = "Build ID used to suffix ephemeral resources."
  default     = ""
  validation {
    condition     = var.cluster_lifecycle == "persistent" || trimspace(var.build_id) != ""
    error_message = "build_id must be set when cluster_lifecycle is ephemeral."
  }
}

################################################################################
# Networking (VPC & Subnets)
################################################################################

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

################################################################################
# Compute (Standalone EC2)
################################################################################

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

################################################################################
# EKS Cluster Configuration
################################################################################

variable "eks_config" {
  description = "Configuration for the optional EKS cluster."
  type = object({
    enabled                       = bool
    cluster_name                  = string
    version                       = string
    enable_ssh_break_glass        = bool
    ssh_key_name                  = string
    ssh_source_security_group_ids = list(string)
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
    enabled                       = false
    cluster_name                  = ""
    version                       = "1.29"
    enable_ssh_break_glass        = false
    ssh_key_name                  = null
    ssh_source_security_group_ids = []
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

variable "addon_replica_counts" {
  description = "Optional map of addon replica counts by addon name."
  type        = map(number)
  default     = {}
}

variable "enable_storage_addons" {
  description = "Whether to install EBS/EFS/snapshot managed add-ons."
  type        = bool
  default     = true
}

################################################################################
# Bootstrap & Break-Glass Settings
################################################################################

variable "bootstrap_mode" {
  description = "When true, use bootstrap-safe node sizing."
  type        = bool
  default     = false
}

variable "bootstrap_node_group" {
  description = "Node group sizing used during bootstrap mode."
  type = object({
    min_size     = number
    desired_size = number
    max_size     = number
  })
  default = {
    min_size     = 3
    desired_size = 3
    max_size     = 5
  }
}

// SSM is the default node access path; SSH is break-glass and should be time-boxed and IP-restricted.
variable "enable_ssh_break_glass" {
  type        = bool
  description = "Enable SSH break-glass access to worker nodes."
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

################################################################################
# IAM & Identity (OIDC / Roles / ESO)
################################################################################

variable "iam_config" {
  description = "Configuration for optional EKS IAM roles and OIDC assume role."
  type = object({
    enabled                                 = bool
    cluster_role_name                       = string
    node_group_role_name                    = string
    oidc_role_name                          = string
    oidc_issuer_url                         = string
    oidc_provider_arn                       = string
    oidc_audience                           = string
    oidc_subject                            = string
    enable_autoscaler_role                  = bool
    autoscaler_role_name                    = string
    autoscaler_policy_arn                   = string
    autoscaler_service_account_namespace    = string
    autoscaler_service_account_name         = string
    enable_lb_controller_role               = bool
    lb_controller_role_name                 = string
    lb_controller_policy_arn                = string
    lb_controller_service_account_namespace = string
    lb_controller_service_account_name      = string
    enable_eso_role                         = optional(bool, false)
    eso_role_name                           = optional(string, "goldenpath-idp-eso-role")
    eso_service_account_namespace           = optional(string, "external-secrets")
    eso_service_account_name                = optional(string, "external-secrets")
  })
  validation {
    condition     = var.iam_config.enabled == false || var.eks_config.enabled == true
    error_message = "iam_config.enabled requires eks_config.enabled to be true."
  }
  default = {
    enabled                                 = false
    cluster_role_name                       = ""
    node_group_role_name                    = ""
    oidc_role_name                          = ""
    oidc_issuer_url                         = ""
    oidc_provider_arn                       = ""
    oidc_audience                           = "sts.amazonaws.com"
    oidc_subject                            = ""
    enable_autoscaler_role                  = false
    autoscaler_role_name                    = "goldenpath-idp-cluster-autoscaler"
    autoscaler_policy_arn                   = ""
    autoscaler_service_account_namespace    = "kube-system"
    autoscaler_service_account_name         = "cluster-autoscaler"
    enable_lb_controller_role               = false
    lb_controller_role_name                 = "goldenpath-idp-aws-load-balancer-controller"
    lb_controller_policy_arn                = ""
    lb_controller_service_account_namespace = "kube-system"
    lb_controller_service_account_name      = "aws-load-balancer-controller"
    enable_eso_role                         = false
    eso_role_name                           = "goldenpath-idp-eso-role"
    eso_service_account_namespace           = "external-secrets"
    eso_service_account_name                = "external-secrets"
  }
}

variable "enable_k8s_resources" {
  type        = bool
  description = "Enable Kubernetes resources managed by Terraform (service accounts). Set true only after kubeconfig is available."
  default     = false
}

################################################################################
# Platform Catalogs (ECR & Secrets)
################################################################################

variable "ecr_repositories" {
  description = "Map of ECR repositories to create."
  type = map(object({
    metadata = object({
      id    = string
      owner = string
      risk  = optional(string, "medium")
    })
  }))
  default = {}
}

variable "app_secrets" {
  description = "Map of application secrets to provision in Secrets Manager."
  type = map(object({
    metadata = object({
      id    = string
      owner = string
      risk  = optional(string, "medium")
    })
    description            = optional(string, "Managed application secret")
    read_principals        = optional(list(string), [])
    write_principals       = optional(list(string), [])
    break_glass_principals = optional(list(string), [])
  }))
  default = {}
}
