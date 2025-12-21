#
resource "aws_network_interface" "instance" {
  subnet_id       = aws_subnet.public.id
  security_groups = [aws_security_group.instance.id]
}

resource "aws_instance" "app" {
  ami           = var.ami_id
  instance_type = var.instance_type
  network_interface {
    network_interface_id = aws_network_interface.instance.id
    device_index         = 0
  }

  tags = {
    "name" = "value"
  }
}
