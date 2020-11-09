data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

data "null_data_source" "lambda_file" {
  inputs = {
    filename = "${path.module}/functions/lambda.py"
  }
}

data "null_data_source" "lambda_archive" {
  inputs = {
    filename = "${path.module}/functions/lambda.zip"
  }
}

data "archive_file" "lambda" {
  type        = "zip"
  source_file = data.null_data_source.lambda_file.outputs.filename
  output_path = data.null_data_source.lambda_archive.outputs.filename
}

data "aws_autoscaling_group" "group" {
  name = var.autoscaling_group_name
}

data "aws_launch_template" "template" {
  name = var.launch_template_name
}
