import json
import logging
import logging.config
from os import environ

import boto3
import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration


class LambdaError(RuntimeError):
    pass


class LaunchTemplateVersionsListSizeMismatch(LambdaError):
    pass


class InstanceRefreshInProgress(LambdaError):
    pass


AUTO_SCALING_GROUP_NAME = environ['AUTO_SCALING_GROUP_NAME']
DESCRIBE_INSTANCE_REFRESHES_MAX_RECORDS = int(environ['DESCRIBE_INSTANCE_REFRESHES_MAX_RECORDS'])
FINISHED_INSTANCE_REFRESH_STATES = ('Cancelled', 'Failed', 'Successful')
LOGGING_LEVEL = environ.get('LOGGING_LEVEL', logging.INFO)
REFRESH_INSTANCE_WARMUP = int(environ['REFRESH_INSTANCE_WARMUP'])
REFRESH_MIN_HEALTHY_PERCENTAGE = int(environ['REFRESH_MIN_HEALTHY_PERCENTAGE'])
REFRESH_SKIP_MATCHING = bool(environ['REFRESH_SKIP_MATCHING'])
SENTRY_DSN = environ.get('SENTRY_DSN')
SSM_PARAMETER_NAME = environ['SSM_PARAMETER_NAME']
UPDATE_MIXED_INSTANCES_POLICY_OVERRIDEN_LAUNCH_TEMPLATES = bool(environ['UPDATE_MIXED_OVERRIDE_LAUNCH_TEMPLATES'])

if SENTRY_DSN:
    sentry_sdk.init(SENTRY_DSN, integrations=[AwsLambdaIntegration()])

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] <%(levelname)s>: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'root': {
        'handlers': ('console',),
        'level': LOGGING_LEVEL,
    },
})
logger = logging.getLogger()

autoscaling = boto3.client('autoscaling')
ec2 = boto3.client('ec2')
ssm = boto3.client('ssm')


def get_current_image_id():
    """Returns current AMI from SSM"""
    param_value = None
    param = ssm.get_parameter(Name=SSM_PARAMETER_NAME)
    value = param['Parameter']['Value']
    if value.startswith('ami-'):
        image_id = value
    else:
        param_value = json.loads(value)
        image_id = param_value['image_id']
    logger.info('Newest image_id is "%s"', image_id)
    return image_id


def get_launch_template_names_and_auto_scaling_group():
    """Returns Launch Template names for Auto Scaling Group"""
    group_description_resp = autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=(AUTO_SCALING_GROUP_NAME,))
    group_details = group_description_resp['AutoScalingGroups'][0]
    mixed_instances_policy = group_details['MixedInstancesPolicy']
    launch_template_names = []

    if 'MixedInstancesPolicy' in group_details:
        launch_template_details = mixed_instances_policy['LaunchTemplate']
        launch_template_names.append(launch_template_details['LaunchTemplateSpecification']['LaunchTemplateName'])

        if UPDATE_MIXED_INSTANCES_POLICY_OVERRIDEN_LAUNCH_TEMPLATES:
            overrides = launch_template_details['Overrides']
            for override in overrides:
                if override_lt_specification := override.get('LaunchTemplateSpecification'):
                    if override_lt_name := override_lt_specification.get('LaunchTemplateName'):
                        launch_template_names.append(override_lt_name)
    else:
        launch_template_names.append(group_details['LaunchTemplate']['LaunchTemplateName'])

    logger.info('Using Launch Templates "%s"', launch_template_names)
    return (launch_template_names, group_description_resp['AutoScalingGroups'][0])


def is_launch_template_updated(image_id, launch_template_name):
    """Checks consistency between $Default and $Latest versions of Launch Template and returns bool wheter versions
    match
    """
    default_and_latest_versions = ec2.describe_launch_template_versions(
        LaunchTemplateName=launch_template_name,
        Versions=('$Default', '$Latest'),
    )
    if (size := len(default_and_latest_versions)) != 2:
        raise LaunchTemplateVersionsListSizeMismatch(
            f'Versions description for $Default and $Latest contains {size} items'
        )
    launch_template_versions = default_and_latest_versions['LaunchTemplateVersions']

    first_image_id = launch_template_versions[0]['LaunchTemplateData']['ImageId']
    second_image_id = launch_template_versions[1]['LaunchTemplateData']['ImageId']

    return first_image_id == second_image_id == image_id


def update_launch_template(image_id, launch_template_name):
    """Creates a new Launch Template version and sets it as default for the Launch Template"""

    def get_instance_refreshes(token=None, max_records=DESCRIBE_INSTANCE_REFRESHES_MAX_RECORDS):
        kwargs = {'AutoScalingGroupName': AUTO_SCALING_GROUP_NAME, 'MaxRecords': max_records}
        if token is not None:
            kwargs['NextToken'] = token
        return autoscaling.describe_instance_refreshes(**kwargs)

    def check_instance_refreshes(instance_refreshes):
        for refresh in instance_refreshes:
            if refresh['Status'] not in FINISHED_INSTANCE_REFRESH_STATES:
                raise InstanceRefreshInProgress(
                    f'Instance refresh "{refresh["InstanceRefreshId"]}" is currently "{refresh["Status"]}"'
                )

    instance_refreshes_resp = get_instance_refreshes()
    check_instance_refreshes(instance_refreshes_resp['InstanceRefreshes'])
    while 'NextToken' in instance_refreshes_resp:
        logger.info('PAGING')
        instance_refreshes_resp = get_instance_refreshes(instance_refreshes_resp['NextToken'])
        check_instance_refreshes(instance_refreshes_resp['InstanceRefreshes'])

    launch_template_resp = ec2.create_launch_template_version(
        LaunchTemplateName=launch_template_name,
        SourceVersion='$Default',
        VersionDescription=f'Automated AMI update to "{image_id}"',
        LaunchTemplateData={
            'ImageId': image_id,
        },
    )
    logger.info('Created a new version of Launch Template\n\n%s', launch_template_resp)
    modify_resp = ec2.modify_launch_template(
        LaunchTemplateName=launch_template_name,
        DefaultVersion=str(launch_template_resp['LaunchTemplateVersion']['VersionNumber']),
    )
    logger.info('Set the new Launch Template version as default\n\n%s', modify_resp)


def start_instance_refresh():
    try:
        refresh_resp = autoscaling.start_instance_refresh(
            AutoScalingGroupName=AUTO_SCALING_GROUP_NAME,
            Strategy='Rolling',
            Preferences={
                'InstanceWarmup': REFRESH_INSTANCE_WARMUP,
                'MinHealthyPercentage': REFRESH_MIN_HEALTHY_PERCENTAGE,
                'SkipMatching': REFRESH_SKIP_MATCHING,
            },
        )
    except autoscaling.exceptions.InstanceRefreshInProgressFault as ex:
        logger.exception(ex)
        return None
    else:
        logger.info('Started instance refresh\n\n%s', refresh_resp)
        return True


def main():
    image_id = get_current_image_id()
    launch_template_names, autoscaling_group = get_launch_template_names_and_auto_scaling_group()
    all_templates_up_to_date = True

    for launch_template_name in launch_template_names:
        if not is_launch_template_updated(image_id, launch_template_name):
            all_templates_up_to_date = False
            logger.info('Launch Template "%s" for Auto Scaling Group "%s" is not up to date',
                        launch_template_name, AUTO_SCALING_GROUP_NAME)
            update_launch_template(image_id, launch_template_name)
        else:
            logger.info('Launch Template "%s" for Auto Scaling Group "%s" is already up to date',
                        launch_template_name, AUTO_SCALING_GROUP_NAME)

    if not all_templates_up_to_date:
        start_instance_refresh()


def handler(event, context):
    try:
        return main()
    except LambdaError as ex:
        logger.error(ex)
        return None


if __name__ == '__main__':
    handler(None, None)
