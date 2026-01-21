################################################################################
# AWS Route53 Module - Variables
################################################################################

variable "domain_name" {
  description = "The domain name for the hosted zone (e.g., goldenpathidp.io)"
  type        = string
}

variable "zone_id" {
  description = "Optional hosted zone ID to use instead of name lookup"
  type        = string
  default     = ""
}

variable "environment" {
  description = "Environment identifier (dev/staging/prod)"
  type        = string
}

variable "create_hosted_zone" {
  description = "Whether to create a new hosted zone or use an existing one"
  type        = bool
  default     = true
}

variable "zone_comment" {
  description = "Comment for the hosted zone"
  type        = string
  default     = "Managed by Terraform"
}

variable "create_wildcard_record" {
  description = "Whether to create a wildcard CNAME record for the environment subdomain"
  type        = bool
  default     = true
}

variable "wildcard_target" {
  description = "Target for the wildcard CNAME record (e.g., Kong LoadBalancer hostname)"
  type        = string
  default     = ""
}

variable "record_ttl" {
  description = "Default TTL for DNS records in seconds"
  type        = number
  default     = 300
}

variable "cname_records" {
  description = "Map of additional CNAME records to create"
  type = map(object({
    target = string
    ttl    = optional(number)
  }))
  default = {}
}

variable "a_records" {
  description = "Map of A records to create. Use '@' for apex domain."
  type = map(object({
    addresses = list(string)
    ttl       = optional(number)
  }))
  default = {}
}

variable "alias_records" {
  description = "Map of alias records for AWS resources (ALB/NLB)"
  type = map(object({
    target                 = string
    zone_id                = string
    evaluate_target_health = optional(bool, true)
  }))
  default = {}
}

variable "tags" {
  description = "Tags to apply to Route53 resources"
  type        = map(string)
  default     = {}
}
