data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/functions/lambda.py"
  output_path = "${path.module}/functions/lambda.zip"
}

data "aws_autoscaling_group" "group" {
  name = var.autoscaling_group_name
}

data "aws_launch_template" "template" {
  name = var.launch_template_name
}
