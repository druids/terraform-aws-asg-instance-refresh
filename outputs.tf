output "asg_arn" {
  value = "${data.aws_autoscaling_group.group.arn}"
}

output "lt_arn" {
  value = "${data.aws_launch_template.template.arn}"
}

output "lt_id" {
  value = "${data.aws_launch_template.template.id}"
}

output "lt_name" {
  value = "${data.aws_launch_template.template.name}"
}
