variable "name" {
  type        = string
  description = "Name tag for the EC2 instance."
}

variable "ami_id" {
  type        = string
  description = "AMI ID to use for the EC2 instance."
}

variable "instance_type" {
  type        = string
  description = "Instance type for the EC2 instance."
}

variable "subnet_id" {
  type        = string
  description = "Subnet ID where the instance will reside."
}

variable "security_group_ids" {
  type        = list(string)
  description = "Security groups attached to the network interface."
  default     = []
}

variable "ssh_key_name" {
  type        = string
  description = "Optional SSH key name for the instance."
  default     = null
}

variable "user_data" {
  type        = string
  description = "Optional user data script."
  default     = null
}

variable "iam_instance_profile" {
  type        = string
  description = "Optional IAM instance profile name."
  default     = null
}

variable "network_interface_description" {
  type        = string
  description = "Description for the ENI."
  default     = "Managed by Terraform"
}

variable "root_volume_size" {
  type        = number
  description = "Size of the root volume in GB."
  default     = 20
}

variable "root_volume_type" {
  type        = string
  description = "Type of the root EBS volume."
  default     = "gp3"
}

variable "root_volume_encrypted" {
  type        = bool
  description = "Whether the root volume is encrypted."
  default     = true
}

variable "tags" {
  type        = map(string)
  description = "Additional tags to apply to the instance and ENI."
  default     = {}
}

variable "environment" {
  type        = string
  description = "Environment name for tagging."
  default     = ""
}
