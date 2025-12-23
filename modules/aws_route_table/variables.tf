variable "vpc_id" {
  type        = string
  description = "ID of the VPC to attach the route table to."
}

variable "name" {
  type        = string
  description = "Name tag for the route table."
  default     = "route-table"
}

variable "gateway_id" {
  type        = string
  description = "Gateway ID used for the default route. Leave empty to skip default routing."
  default     = ""
}

variable "nat_gateway_id" {
  type        = string
  description = "NAT gateway ID used for the default route. Leave empty to skip default routing."
  default     = ""
}

variable "destination_cidr_block" {
  type        = string
  description = "CIDR block for the default route."
  default     = "0.0.0.0/0"
}

variable "subnet_ids" {
  type        = list(string)
  description = "List of subnet IDs to associate with this route table."
  default     = []
}

variable "tags" {
  type        = map(string)
  description = "Additional tags to apply to the route table."
  default     = {}
}

variable "route_target" {
  type        = string
  description = "Internal validation placeholder."
  default     = ""
  validation {
    condition = (
      (var.gateway_id != "" && var.nat_gateway_id == "") ||
      (var.gateway_id == "" && var.nat_gateway_id != "")
    )
    error_message = "Set exactly one of gateway_id or nat_gateway_id."
  }
}

variable "environment" {
  type        = string
  description = "Environment name for tagging."
  default     = ""
}
