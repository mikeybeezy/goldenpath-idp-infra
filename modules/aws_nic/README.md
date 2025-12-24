# Network Interface Module

## Purpose
Creates a standalone ENI in a subnet with optional static private IPs.

## Inputs
- `name` (string): Name tag for the ENI.
- `subnet_id` (string): Subnet ID.
- `security_group_ids` (list(string), optional).
- `private_ips` (list(string), optional).
- `description` (string, optional).
- `tags` (map(string), optional).
- `environment` (string, optional).

## Outputs
- `network_interface_id`: ENI ID.

## Notes
- Useful when attaching ENIs to instances or other resources later.
