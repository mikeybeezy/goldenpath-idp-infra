locals {
  subnet_map = {
    for idx, subnet_id in var.subnet_ids :
    idx => subnet_id
  }
}

resource "aws_route_table" "this" {
  vpc_id = var.vpc_id

  dynamic "route" {
    for_each = var.gateway_id != "" ? [var.gateway_id] : []
    content {
      cidr_block = var.destination_cidr_block
      gateway_id = route.value
    }
  }

  tags = merge(
    {
      Name = var.name
    },
    var.tags,
  )
}

resource "aws_route_table_association" "this" {
  for_each = local.subnet_map

  route_table_id = aws_route_table.this.id
  subnet_id      = each.value
}
