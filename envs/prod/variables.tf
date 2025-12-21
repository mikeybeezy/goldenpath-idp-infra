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
