variable "vpc_cidr" {
  type        = string
  description = "CIDR block used for the VPC."
  default     = "172.16.0.0/16"
}

variable "vpc_tag" {
  type        = string
  description = "Name tag for the VPC."
  default     = "goldenpath-vpc"
}

variable "tags" {
  type        = map(string)
  description = "Additional tags merged onto all resources."
  default     = {}
}

variable "create_internet_gateway" {
  type        = bool
  description = "Whether to create an Internet Gateway for this VPC."
  default     = true
}

variable "existing_internet_gateway_id" {
  type        = string
  description = "If provided, reuse this IGW instead of creating a new one."
  default     = ""
}

variable "create_public_route_table" {
  type        = bool
  description = "Whether to create a public route table."
  default     = true
}

variable "public_route_cidr_block" {
  type        = string
  description = "Destination CIDR for the default route in the public route table."
  default     = "0.0.0.0/0"
}

variable "public_route_table_name" {
  type        = string
  description = "Name tag applied to the public route table."
  default     = "public-route-table"
}
