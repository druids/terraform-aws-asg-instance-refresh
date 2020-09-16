import json
import logging
import logging.config
from os import environ

import boto3


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
SSM_PARAMETER_NAME = environ['SSM_PARAMETER_NAME']

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
    param = ssm.get_parameter(Name=SSM_PARAMETER_NAME)
    param_value = json.loads(param['Parameter']['Value'])
    image_id = param_value['image_id']
    logger.info('Newest image_id is "%s"', image_id)
    return param_value['image_id']


def get_launch_template_name():
    """Returns Launch Template name for Auto Scaling Group"""
    group_description_resp = autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=(AUTO_SCALING_GROUP_NAME,))
    launch_template_details = group_description_resp['AutoScalingGroups'][0]['MixedInstancesPolicy']['LaunchTemplate']
    launch_template_name = launch_template_details['LaunchTemplateSpecification']['LaunchTemplateName']
    logger.info('Using Launch Template "%s"', launch_template_name)
    return launch_template_name


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


def main():
    image_id = get_current_image_id()
    launch_template_name = get_launch_template_name()
    if launch_template_state := is_launch_template_updated(image_id, launch_template_name):
        logger.info('Launch Template for Auto Scaling Group "%s" is already up to date', AUTO_SCALING_GROUP_NAME)
        return launch_template_state

    logger.info('Launch Template for Auto Scaling Group "%s" is not up to date', AUTO_SCALING_GROUP_NAME)
    update_launch_template(image_id, launch_template_name)

    try:
        refresh_resp = autoscaling.start_instance_refresh(
            AutoScalingGroupName=AUTO_SCALING_GROUP_NAME,
            Strategy='Rolling',
            Preferences={
                'InstanceWarmup': REFRESH_INSTANCE_WARMUP,
                'MinHealthyPercentage': REFRESH_MIN_HEALTHY_PERCENTAGE,
            },
        )
    except autoscaling.exceptions.InstanceRefreshInProgressFault as ex:
        logger.exception(ex)
        return None
    else:
        logger.info('Started instance refresh\n\n%s', refresh_resp)


def handler(event, context):
    try:
        return main()
    except LambdaError as ex:
        logger.error(ex)
        return None


if __name__ == '__main__':
    handler(None, None)
