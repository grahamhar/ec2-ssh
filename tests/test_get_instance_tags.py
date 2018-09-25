from ec2_ssh import ec2_helpers as ec2_helpers
import pytest
from unittest.mock import Mock
from collections import defaultdict


@pytest.fixture(autouse=True)
def reset_global_vars():
    ec2_helpers.ec2_client = None
    ec2_helpers.selected_tag_name = None
    ec2_helpers.selected_tag_value = None
    ec2_helpers.instance_tags = defaultdict(set)
    ec2_helpers.tag_instance_ips = defaultdict(lambda: defaultdict(list))


def test_returns_results_as_expected_when_tags_empty():
    """When there are no tags an empty dict should be returned"""
    boto3_mock = Mock()
    boto3_mock().describe_tags.return_value = {'Tags': []}
    ec2_helpers.get_ec2_client = boto3_mock

    assert ec2_helpers.get_instance_tags() == {}
    assert ec2_helpers.instance_tags == {}


def test_returns_results_as_expected_when_duplicate_tags():
    """When there are is a single tag it should be returned"""
    boto3_mock = Mock()
    boto3_mock().describe_tags.return_value = {
        'Tags': [{'Key': 'Name', 'Value': 'value1'}, {'Key': 'Name', 'Value': 'value1'}]}
    ec2_helpers.get_ec2_client = boto3_mock

    assert ec2_helpers.get_instance_tags() == {'Name': {'value1'}}
    assert ec2_helpers.instance_tags == {'Name': {'value1'}}


def test_returns_results_as_expected_when_duplicate_tag_values():
    """When there are is a repeated tag key with different values it should return a dict with a single key and multiple values in the set"""
    boto3_mock = Mock()
    boto3_mock().describe_tags.return_value = {
        'Tags': [{'Key': 'Name', 'Value': 'value1'}, {'Key': 'Name', 'Value': 'value2'}]}
    ec2_helpers.get_ec2_client = boto3_mock

    assert ec2_helpers.get_instance_tags() == {'Name': {'value1', 'value2'}}
    assert ec2_helpers.instance_tags == {'Name': {'value1', 'value2'}}


def test_returns_results_as_expected_when_multiple_keys():
    """When there are two tag keys with same values it should return a dict with a two keys and the same single value in the set"""
    boto3_mock = Mock()
    boto3_mock().describe_tags.return_value = {
        'Tags': [{'Key': 'Name1', 'Value': 'value'}, {'Key': 'Name2', 'Value': 'value'}]}
    ec2_helpers.get_ec2_client = boto3_mock

    assert ec2_helpers.get_instance_tags() == {'Name1': {'value'}, 'Name2': {'value'}}
    assert ec2_helpers.instance_tags == {'Name1': {'value'}, 'Name2': {'value'}}
