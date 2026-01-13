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

variable "environment" {
  type        = string
  description = "Environment name for tagging."
  default     = ""
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

variable "private_route_table_ids" {
  type        = list(string)
  description = "List of private route table IDs for associating gateway endpoints."
  default     = []
}

variable "enable_s3_endpoint" {
  type        = bool
  description = "Whether to create a VPC Gateway Endpoint for S3."
  default     = false
}

variable "enable_ecr_endpoints" {
  type        = bool
  description = "Whether to create VPC Interface Endpoints for ECR (API and DKR)."
  default     = false
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "List of private subnet IDs for Interface Endpoints (required if enable_ecr_endpoints is true)."
  default     = []
}

variable "aws_region" {
  type        = string
  description = "AWS region for endpoint service names."
  default     = "eu-west-2"
}
