import pytest

from unittest.mock import call, patch

from ec2_ssh import EC2HostFinder


def test_get_instances():
    """It should return a list of instance ip addresses and use the default tag name and provided tag value"""
    with patch('ec2_ssh.ec2_client') as mock_boto_again:
        expected_result = ['1.1.1.1', '1.1.1.2', '1.1.1.3', '1.1.1.4']
        mock_boto_again.describe_instances.return_value = {
            'Reservations': [
                {'Instances': [{'NetworkInterfaces': [{'PrivateIpAddress': '1.1.1.1'}]}, {'NetworkInterfaces': [{'PrivateIpAddress': '1.1.1.2'}]}]},
                {'Instances': [{'NetworkInterfaces': [{'PrivateIpAddress': '1.1.1.3'}, {'PrivateIpAddress': '1.1.1.4'}]}]}

            ]}
        ec2_host_finder = EC2HostFinder()
        assert sorted(expected_result) == sorted(ec2_host_finder.get_ec2_instances(tag_value='fake'))
        assert mock_boto_again.describe_instances.call_args_list == [call(DryRun=False, Filters=[{'Name': 'tag:Name', 'Values': ['fake']}], MaxResults=1000)]


def test_get_instances_custom_tag():
    """It should return a list of instanceids and use the provided tag name and provided tag value"""
    with patch('ec2_ssh.ec2_client') as mock_boto_again:
        expected_result = ['1.1.1.1', '1.1.1.2', '1.1.1.3', '1.1.1.4']
        mock_boto_again.describe_instances.return_value = {
            'Reservations': [
                {'Instances': [{'NetworkInterfaces': [{'PrivateIpAddress': '1.1.1.1'}]}, {'NetworkInterfaces': [{'PrivateIpAddress': '1.1.1.2'}]}]},
                {'Instances': [{'NetworkInterfaces': [{'PrivateIpAddress': '1.1.1.3'}, {'PrivateIpAddress': '1.1.1.4'}]}]}

            ]}
        ec2_host_finder = EC2HostFinder()
        assert sorted(expected_result) == sorted(ec2_host_finder.get_ec2_instances(tag_value='fake', tag_filter="TestKeyName"))
        assert mock_boto_again.describe_instances.call_args_list == [call(DryRun=False, Filters=[{'Name': 'tag:TestKeyName', 'Values': ['fake']}], MaxResults=1000)]


def test_get_tags_defaults():
    """It should return only unique tags and the default tag name should be used to filter"""
    with patch('ec2_ssh.ec2_client') as mock_boto:
        expected_result = ['value_1', 'value_2']
        mock_boto.describe_tags.return_value = {
            'Tags': [{
                'Key': 'Name',
                'ResourceType': 'instance',
                'Value': 'value_1'
            }, {
                'Key': 'Name',
                'ResourceType': 'instance',
                'Value': 'value_2'
            }, {
                'Key': 'Name',
                'ResourceType': 'instance',
                'Value': 'value_2'
            }
            ]}
        ec2_host_finder = EC2HostFinder()
        assert sorted(expected_result) == sorted(ec2_host_finder.get_unique_instance_tag_values())
        mock_boto.describe_tags.assert_called_with(DryRun=False, Filters=[{'Name': 'key', 'Values': ['Name']}, {'Name': 'resource-type', 'Values': ['instance', 'reserved-instances']}], MaxResults=1000)


def test_get_tags_override_tag():
    """It should return only unique tags and the provided tag name should be used to filter"""
    with patch('ec2_ssh.ec2_client') as mock_boto:
        expected_result = ['value_1', 'value_2']
        mock_boto.describe_tags.return_value = {
            'Tags': [{
                'Key': 'Thing',
                'ResourceType': 'instance',
                'Value': 'value_1'
            }, {
                'Key': 'Thing',
                'ResourceType': 'instance',
                'Value': 'value_2'
            }, {
                'Key': 'Thing',
                'ResourceType': 'instance',
                'Value': 'value_2'
            }
            ]}
        ec2_host_finder = EC2HostFinder()
        assert sorted(expected_result) == sorted(ec2_host_finder.get_unique_instance_tag_values(tag_filter='Thing'))
        assert mock_boto.describe_tags.call_args_list == [call(DryRun=False, Filters=[{'Name': 'key', 'Values': ['Thing']}, {'Name': 'resource-type', 'Values': ['instance', 'reserved-instances']}], MaxResults=1000)]


def test_get_tag_keys_defaults():
    with patch('ec2_ssh.ec2_client') as mock_boto:
        expected_result = ['key1', 'key2']
        mock_boto.describe_tags.return_value = {
            'Tags': [{
                'Key': 'key1',
                'ResourceType': 'instance',
                'Value': 'value_1'
            }, {
                'Key': 'key2',
                'ResourceType': 'instance',
                'Value': 'value_2'
            }, {
                'Key': 'key1',
                'ResourceType': 'instance',
                'Value': 'value_2'
            }
            ]}
        ec2_host_finder = EC2HostFinder()
        assert sorted(expected_result) == sorted(ec2_host_finder.get_unique_instance_tag_keys())
        assert mock_boto.describe_tags.call_args_list == [call(DryRun=False,
                                                               Filters=[{'Name': 'resource-type',
                                                                         'Values': ['instance', 'reserved-instances']}],
                                                               MaxResults=1000)]
