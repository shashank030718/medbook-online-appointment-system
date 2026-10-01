resource "aws_security_group" "alb" {
  name        = "medbook-alb-sg"
  description = "Allow HTTP traffic to MedBook ALB"
  vpc_id      = aws_vpc.medbook.id

  ingress {
    description = "HTTP from Internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "medbook-alb-sg"
  }
}




resource "aws_security_group" "ecs" {
  name        = "medbook-ecs-sg"
  description = "Allow traffic from MedBook ALB"
  vpc_id      = aws_vpc.medbook.id

  ingress {
    description     = "Flask app traffic from ALB"
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "medbook-ecs-sg"
  }
}





resource "aws_security_group" "rds" {
  name        = "medbook-rds-sg"
  description = "Allow MySQL traffic from MedBook ECS"
  vpc_id      = aws_vpc.medbook.id

  ingress {
    description     = "MySQL from ECS"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "medbook-rds-sg"
  }
}