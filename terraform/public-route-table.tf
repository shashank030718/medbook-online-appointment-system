resource "aws_route_table" "public" {
  vpc_id = aws_vpc.medbook.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.medbook.id
  }

  tags = {
    Name = "medbook-public-rt"
  }
}