locals {
  subnet_map = {
    for idx, subnet_id in var.subnet_ids :
    idx => subnet_id
  }

  environment_tags = var.environment != "" ? { Environment = var.environment } : {}
  route_target     = var.gateway_id != "" ? "igw" : (var.nat_gateway_id != "" ? "nat" : "")
}

resource "aws_route_table" "this" {
  vpc_id = var.vpc_id

  dynamic "route" {
    for_each = local.route_target != "" ? [local.route_target] : []
    content {
      cidr_block     = var.destination_cidr_block
      gateway_id     = route.value == "igw" ? var.gateway_id : null
      nat_gateway_id = route.value == "nat" ? var.nat_gateway_id : null
    }
  }

  tags = merge(
    {
      Name = var.name
    },
    var.tags,
    local.environment_tags,
  )
}

resource "aws_route_table_association" "this" {
  for_each = local.subnet_map

  route_table_id = aws_route_table.this.id
  subnet_id      = each.value
}
