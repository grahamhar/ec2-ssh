import os

from collections import defaultdict

import boto3
import botocore

from awscli.customizations.assumerole import JSONFileCache
from click import UsageError

boto3_session = None
current_aws_profile = None
ec2_client = None
instance_tags = defaultdict(set)


def get_aws_session(aws_profile):
    global boto3_session
    boto3_session = botocore.session.Session(profile=aws_profile)
    credential_provider = boto3_session.get_component('credential_provider')
    provider = credential_provider.get_provider('assume-role')
    provider.cache = JSONFileCache()


def get_region(session):
    config = session.get_scoped_config()
    if 'region' not in config.keys():
        config['region'] = os.getenv('AWS_REGION', os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))
    return config['region']


def get_ec2_client():
    global boto3_session, current_aws_profile, ec2_client
    aws_profile = os.getenv('AWS_PROFILE', os.getenv('AWS_DEFAULT_PROFILE', 'default'))
    if current_aws_profile != aws_profile:
        current_aws_profile = aws_profile
        boto3_session = None
    if ec2_client is None or boto3_session is None:
        try:
            get_aws_session(current_aws_profile)
            aws_region = get_region(boto3_session)
            credentials = boto3_session.get_credentials()
            ec2_client = boto3.client(service_name='ec2', region_name=aws_region, aws_access_key_id=credentials.access_key, aws_secret_access_key=credentials.secret_key, aws_session_token=credentials.token)
        except AttributeError:
            raise UsageError(
                '\nA valid AWS Profile could not be found.\nPlease check you have a "default" profile in your AWS credentials file or the "AWS_PROFILE" environment variable is set')
    return ec2_client


def get_ec2_instance_ips(tag_key, tag_value):
    # TODO: handle paginated responses
    instance_ips = []
    if tag_key is not None and tag_value is not None:
        tag_key = tag_key.replace('_COLON_', ':')
        response = get_ec2_client().describe_instances(
            Filters=[
                {
                    'Name': 'tag:{}'.format(tag_key),
                    'Values': [
                        tag_value,
                    ]
                },
            ],
            DryRun=False,
            MaxResults=1000
        )
        instance_ips = [network_interface['PrivateIpAddress'] for reservation in response['Reservations'] for instance in
                        reservation['Instances'] for network_interface in instance['NetworkInterfaces']]
        instance_ips.extend(['all', 'random'])
    return sorted(instance_ips)


def get_instance_tags():
    # TODO: handle paginated responses
    global instance_tags
    if not instance_tags:
        response = get_ec2_client().describe_tags(MaxResults=1000, DryRun=False,
                                                  Filters=[{'Name': 'resource-type',
                                                            'Values': ['instance', 'reserved-instances']}])
        for tag in response['Tags']:
            key = tag['Key'].replace(':', '_COLON_')
            instance_tags[key].add(tag['Value'])
    return instance_tags
