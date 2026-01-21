################################################################################
# AWS Route53 Module
#
# Manages Route53 hosted zones and DNS records for the platform.
# Supports both apex domain and environment-specific subdomains.
################################################################################

################################################################################
# Hosted Zone
################################################################################

resource "aws_route53_zone" "main" {
  count = var.create_hosted_zone ? 1 : 0

  name    = var.domain_name
  comment = var.zone_comment

  tags = merge(
    var.tags,
    {
      Name = var.domain_name
    }
  )
}

# Use existing hosted zone if not creating a new one
data "aws_route53_zone" "by_id" {
  count = (!var.create_hosted_zone && var.zone_id != "") ? 1 : 0

  zone_id      = var.zone_id
  private_zone = false
}

data "aws_route53_zone" "existing" {
  count = (var.create_hosted_zone || var.zone_id != "") ? 0 : 1

  name         = var.domain_name
  private_zone = false
}

locals {
  zone_id = var.create_hosted_zone ? aws_route53_zone.main[0].zone_id : (
    var.zone_id != "" ? data.aws_route53_zone.by_id[0].zone_id : data.aws_route53_zone.existing[0].zone_id
  )
}

################################################################################
# DNS Records
################################################################################

# Wildcard CNAME record for environment subdomain (e.g., *.dev.goldenpathidp.io)
resource "aws_route53_record" "wildcard_cname" {
  count = var.create_wildcard_record && var.wildcard_target != "" ? 1 : 0

  zone_id = local.zone_id
  name    = "*.${var.environment}.${var.domain_name}"
  type    = "CNAME"
  ttl     = var.record_ttl

  records = [var.wildcard_target]
}

# Additional CNAME records
resource "aws_route53_record" "cname" {
  for_each = var.cname_records

  zone_id = local.zone_id
  name    = "${each.key}.${var.domain_name}"
  type    = "CNAME"
  ttl     = each.value.ttl != null ? each.value.ttl : var.record_ttl

  records = [each.value.target]
}

# A records (for apex domain or specific hosts)
resource "aws_route53_record" "a_record" {
  for_each = var.a_records

  zone_id = local.zone_id
  name    = each.key == "@" ? var.domain_name : "${each.key}.${var.domain_name}"
  type    = "A"
  ttl     = each.value.ttl != null ? each.value.ttl : var.record_ttl

  records = each.value.addresses
}

# Alias records (for AWS resources like ALB/NLB)
resource "aws_route53_record" "alias" {
  for_each = var.alias_records

  zone_id = local.zone_id
  name    = each.key == "@" ? var.domain_name : "${each.key}.${var.domain_name}"
  type    = "A"

  alias {
    name                   = each.value.target
    zone_id                = each.value.zone_id
    evaluate_target_health = each.value.evaluate_target_health
  }
}
