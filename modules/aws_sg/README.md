# Security Group Module

## Purpose
Creates a security group with HTTPS ingress and open egress.

## Inputs
- `name` (string): Security group name.
- `description` (string, optional): Description text.
- `vpc_id` (string): VPC ID.
- `ingress_cidr_blocks` (list(string), optional): IPv4 CIDRs for port 443.
- `ingress_ipv6_cidr_blocks` (list(string), optional): IPv6 CIDRs for port 443.
- `tags` (map(string), optional): Extra tags.
- `environment` (string, optional): Environment tag.

## Outputs
- `security_group_id`

## Notes
- Defaults allow HTTPS from all IPv4/IPv6. Tighten for non-dev.
