from collections import defaultdict

import boto3


ec2_client = None
instance_tags = defaultdict(set)


def get_ec2_client():
    global ec2_client
    if ec2_client is None:
        ec2_client = boto3.client('ec2')
    return ec2_client


def get_ec2_instance_ips(tag_key, tag_value):
    # TODO: handle paginated responses
    instance_ips = []
    if tag_key is not None and tag_value is not None:
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
            instance_tags[tag['Key']].add(tag['Value'])
    return instance_tags

