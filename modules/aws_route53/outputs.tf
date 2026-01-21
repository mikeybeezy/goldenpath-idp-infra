################################################################################
# AWS Route53 Module - Outputs
################################################################################

output "zone_id" {
  description = "The hosted zone ID"
  value       = local.zone_id
}

output "zone_name" {
  description = "The domain name of the hosted zone"
  value       = var.domain_name
}

output "name_servers" {
  description = "List of name servers for the hosted zone (use these in your domain registrar)"
  value = var.create_hosted_zone ? aws_route53_zone.main[0].name_servers : (
    var.zone_id != "" ? data.aws_route53_zone.by_id[0].name_servers : data.aws_route53_zone.existing[0].name_servers
  )
}

output "wildcard_fqdn" {
  description = "The FQDN of the wildcard record"
  value       = var.create_wildcard_record && var.wildcard_target != "" ? "*.${var.environment}.${var.domain_name}" : null
}
