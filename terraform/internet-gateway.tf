resource "aws_internet_gateway" "medbook" {
  vpc_id = aws_vpc.medbook.id

  tags = {
    Name = "medbook-igw"
  }
}