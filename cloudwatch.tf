resource "aws_cloudwatch_event_rule" "rule" {
  name                = "${var.cloudwatch_event_rule_name}"
  schedule_expression = "${var.cloudwatch_event_rule_schedule_expression}"
}

resource "aws_cloudwatch_event_target" "refresh_lambda" {
  rule = "${aws_cloudwatch_event_rule.rule.id}"
  arn  = "${aws_lambda_function.refresh.arn}"
}
