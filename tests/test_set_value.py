import ec2_ssh
import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def reset_global_vars():
    ec2_ssh.instance_tag_value = ''
    ec2_ssh.instance_key = 'Name'
    ec2_ssh.instance_tag_keys = []
    ec2_ssh.instance_tag_values = {}


@patch('ec2_ssh.EC2HostFinder.get_unique_instance_tag_values')
def test_set_value_valid(mock_unique_values, capsys):
    """When the entered value exists as a tag value the prompt should be updated and it should be used as the default value"""
    mock_unique_values.return_value = ['value3', 'value2', 'avalue1']
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    ec2_host_finder.do_set_value('value2')
    assert mock_unique_values.call_count == 1
    assert capsys.readouterr().out == 'Tag value set to: value2\n'


@patch('ec2_ssh.EC2HostFinder.get_unique_instance_tag_values')
def test_set_value_invalid(mock_unique_values, capsys):
    """Only the matching values should be returned from the instance_tag_keys and should be sorted"""
    mock_unique_values.return_value = ['value3', 'value2', 'avalue1']
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    ec2_host_finder.do_set_value('missing')
    assert mock_unique_values.call_count == 1
    assert capsys.readouterr().out == 'Unknown value for tag value, it remains set to: ''\n'


@patch('ec2_ssh.EC2HostFinder.get_unique_instance_tag_values')
def test_set_value_no_update(mock_unique_values, capsys):
    """When the instance_tag_values is populated it should not be updated by calling ec2 and the value should be set"""
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    ec2_ssh.instance_tag_values = {'Name': ['value3', 'value2', 'avalue1']}
    ec2_host_finder.do_set_value('value2')
    assert mock_unique_values.call_count == 0
    assert capsys.readouterr().out == 'Tag value set to: value2\n'


@patch('ec2_ssh.EC2HostFinder.get_unique_instance_tag_values')
def test_set_value_complete_valid(mock_unique_values):
    """Only the matching values should be returned from the instance_tag_keys and should be sorted"""
    mock_unique_values.return_value = ['value3', 'value2', 'avalue1']
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    assert ec2_host_finder.complete_set_value('value', None, None, None) == ['value2', 'value3']
    assert mock_unique_values.call_count == 1


@patch('ec2_ssh.EC2HostFinder.get_unique_instance_tag_values')
def test_set_value_complete_no_match(mock_unique_values):
    """Only the matching values should be returned from the instance_tag_keys and should be sorted"""
    mock_unique_values.return_value = ['value3', 'value2', 'avalue1']
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    assert ec2_host_finder.complete_set_value('missing', None, None, None) == []
    assert mock_unique_values.call_count == 1


@patch('ec2_ssh.EC2HostFinder.get_unique_instance_tag_values')
def test_set_value_complete_no_update(mock_unique_values):
    """When the instance_tag_values is populated it should not be updated by calling ec2 and matching items should
    be returned"""
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    ec2_ssh.instance_tag_values = {'Name': ['value3', 'value2', 'avalue1']}
    assert ec2_host_finder.complete_set_value('value', None, None, None) == ['value2', 'value3']
    assert mock_unique_values.call_count == 0
