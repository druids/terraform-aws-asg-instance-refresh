terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

resource "aws_vpc" "vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "subnet" {
  cidr_block = "10.0.0.0/24"
  vpc_id     = aws_vpc.vpc.id
}

resource "aws_launch_template" "tpl" {
  name          = "tpl"
  image_id      = "ami-06c755ec615b860ac"
  instance_type = "t3.nano"
}

resource "aws_autoscaling_group" "grp" {
  max_size         = 1
  min_size         = 1
  desired_capacity = 1

  vpc_zone_identifier = [aws_subnet.subnet.id]

  mixed_instances_policy {
    launch_template {
      launch_template_specification {
        launch_template_name = aws_launch_template.tpl.name
      }
    }
  }
}

module "refresh" {
  source     = "../"
  depends_on = [aws_launch_template.tpl, aws_autoscaling_group.grp]

  launch_template_name   = aws_launch_template.tpl.name
  autoscaling_group_name = aws_autoscaling_group.grp.name
}

output "asg_arn" {
  value = module.refresh.asg_arn
}

output "lt_arn" {
  value = module.refresh.lt_arn
}

output "lt_id" {
  value = module.refresh.lt_id
}

output "lt_name" {
  value = module.refresh.lt_name
}
