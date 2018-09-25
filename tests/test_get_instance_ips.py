from ec2_ssh import ec2_helpers as ec2_helpers
import pytest
from unittest.mock import Mock
from collections import defaultdict


@pytest.fixture(autouse=True)
def reset_global_vars():
    ec2_helpers.ec2_client = None


def test_returns_results_as_expected_no_tags():
    """When there are no tags set an empty list should be returned"""
    boto3_mock = Mock()
    boto3_mock().describe_instances.return_value = {
        'Reservations': [{'Instances': [{'NetworkInterfaces': [{'PrivateIpAddress': '0.0.0.0'}]}]}]}
    ec2_helpers.get_ec2_client = boto3_mock

    assert ec2_helpers.get_ec2_instance_ips(None, None) == []


def test_returns_results_as_expected_single():
    """When there is a single reservation with a single instance with a single interface it should return 3 items"""
    boto3_mock = Mock()
    boto3_mock().describe_instances.return_value = {
        'Reservations': [{'Instances': [{'NetworkInterfaces': [{'PrivateIpAddress': '0.0.0.0'}]}]}]}
    ec2_helpers.get_ec2_client = boto3_mock

    assert ec2_helpers.get_ec2_instance_ips('Fake', 'Fake') == ['0.0.0.0', 'all', 'random']


def test_returns_results_as_expected_multi_interfaces():
    """When there is a single reservation with a single instance with a two interface it should return 4 items"""
    boto3_mock = Mock()
    boto3_mock().describe_instances.return_value = {
        'Reservations': [
            {'Instances': [{'NetworkInterfaces': [{'PrivateIpAddress': '1.1.1.1'}, {'PrivateIpAddress': '0.0.0.0'}]}]}]}
    ec2_helpers.get_ec2_client = boto3_mock

    assert ec2_helpers.get_ec2_instance_ips('Fake', 'Fake') == ['0.0.0.0', '1.1.1.1', 'all', 'random']
