variable "vpc_id" {
  type        = string
  description = "ID of the VPC where subnets will be created."
}

variable "public_subnets" {
  type = list(object({
    name              = string
    cidr_block        = string
    availability_zone = string
    tags              = optional(map(string))
  }))
  description = "List of public subnet definitions."
  default     = []
}

variable "private_subnets" {
  type = list(object({
    name              = string
    cidr_block        = string
    availability_zone = string
    tags              = optional(map(string))
  }))
  description = "List of private subnet definitions."
  default     = []
}

variable "tags" {
  type        = map(string)
  description = "Common tags applied to every subnet."
  default     = {}
}

variable "environment" {
  type        = string
  description = "Environment name for tagging."
  default     = ""
}
