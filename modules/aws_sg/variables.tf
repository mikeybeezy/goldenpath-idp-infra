variable "name" {
  type        = string
  description = "Name of the security group."
}

variable "description" {
  type        = string
  description = "Description for the security group."
  default     = "Managed by Terraform"
}

variable "vpc_id" {
  type        = string
  description = "ID of the VPC to associate the security group with."
}

variable "ingress_cidr_blocks" {
  type        = list(string)
  description = "CIDR blocks allowed to reach port 443."
  default     = ["0.0.0.0/0"]
}

variable "ingress_ipv6_cidr_blocks" {
  type        = list(string)
  description = "IPv6 CIDR blocks allowed to reach port 443."
  default     = ["::/0"]
}

variable "tags" {
  type        = map(string)
  description = "Additional tags to apply to the security group."
  default     = {}
}

variable "environment" {
  type        = string
  description = "Environment name for tagging."
  default     = ""
}
