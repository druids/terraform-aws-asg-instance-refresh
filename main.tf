data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

data "aws_autoscaling_group" "group" {
  name = var.autoscaling_group_name
}
