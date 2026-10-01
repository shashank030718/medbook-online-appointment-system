resource "aws_ecs_cluster" "medbook" {
  name = "medbook-cluster"

  tags = {
    Name = "medbook-cluster"
  }
}



resource "aws_ecs_task_definition" "medbook" {
  family                   = "medbook-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  cpu    = "256"
  memory = "512"

  execution_role_arn = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name      = "medbook"
      image     = "621788589162.dkr.ecr.ap-south-1.amazonaws.com/medbook:latest"
      essential = true

      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "DB_HOST"
          value = aws_db_instance.medbook.address
        },
        {
          name  = "DB_USER"
          value = var.db_username
        },
        {
          name  = "DB_NAME"
          value = "medbook"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"

        options = {
          awslogs-group         = aws_cloudwatch_log_group.medbook.name
          awslogs-region        = "ap-south-1"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  tags = {
    Name = "medbook-task"
  }
}