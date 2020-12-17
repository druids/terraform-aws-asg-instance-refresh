resource "aws_lambda_function" "refresh" {
  filename = data.archive_file.lambda.output_path

  function_name    = var.lambda_name
  handler          = "lambda.handler"
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.8"
  timeout          = var.lambda_timeout
  source_code_hash = data.archive_file.lambda.output_base64sha256

  description = var.lambda_description

  environment {
    variables = {
      AUTO_SCALING_GROUP_NAME                 = var.autoscaling_group_name
      DESCRIBE_INSTANCE_REFRESHES_MAX_RECORDS = var.describe_instance_refreshes_max_records
      REFRESH_INSTANCE_WARMUP                 = var.instance_refresh_instance_warmup
      REFRESH_MIN_HEALTHY_PERCENTAGE          = var.instance_refresh_min_healthy_percentage
      SSM_PARAMETER_NAME                      = var.ami_ssm_parameter
    }
  }
}

resource "aws_lambda_permission" "allow_cloudwatch_events" {
  statement_id  = "AllowCloudWatchEventsInvokeFunction"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.refresh.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.rule.arn
}
