locals {
  environment_tags = var.environment != "" ? { Environment = var.environment } : {}
}

resource "aws_network_interface" "instance" {
  subnet_id       = var.subnet_id
  security_groups = var.security_group_ids
  description     = var.network_interface_description

  tags = merge(
    {
      Name = "${var.name}-eni"
    },
    var.tags,
    local.environment_tags,
  )
}

resource "aws_instance" "app" {
  ami                  = var.ami_id
  instance_type        = var.instance_type
  key_name             = var.ssh_key_name
  user_data            = var.user_data
  iam_instance_profile = var.iam_instance_profile

  network_interface {
    network_interface_id = aws_network_interface.instance.id
    device_index         = 0
  }

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = var.root_volume_type
    encrypted   = var.root_volume_encrypted
  }

  tags = merge(
    {
      Name = var.name
    },
    var.tags,
    local.environment_tags,
  )
}
