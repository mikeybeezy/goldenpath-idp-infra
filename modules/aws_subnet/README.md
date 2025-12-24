# Subnet Module

## Purpose
Creates public and private subnets in a VPC from declarative lists.

## Inputs
- `vpc_id` (string): VPC ID to attach subnets to.
- `public_subnets` (list(object), optional): Public subnet definitions.
- `private_subnets` (list(object), optional): Private subnet definitions.
- `tags` (map(string), optional): Common tags for all subnets.
- `environment` (string, optional): Environment tag.

## Outputs
- `public_subnet_ids`
- `private_subnet_ids`

## Notes
- Each subnet entry requires `name`, `cidr_block`, and `availability_zone`.
