import ec2_ssh
import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def reset_global_vars():
    ec2_ssh.instance_key_value = ''
    ec2_ssh.instance_key = 'Name'
    ec2_ssh.instance_tag_keys = []


@patch('ec2_ssh.EC2HostFinder.get_unique_instance_tag_keys')
def test_set_key_valid(mock_unique_tags, capsys):
    """When the entered key exists as a tag key the prompt should be updated and it should be used as the default key"""
    mock_unique_tags.return_value = ['Name', 'Environment', 'Department']
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    ec2_host_finder.do_set_key('Environment')
    assert mock_unique_tags.call_count == 1
    assert capsys.readouterr().out == 'Tag key value set to: Environment\n'


@patch('ec2_ssh.EC2HostFinder.get_unique_instance_tag_keys')
def test_set_key_invalid(mock_unique_tags, capsys):
    """When the entered key does not exist as a tag key the prompt should stay the same and an error should be printed"""
    mock_unique_tags.return_value = ['Name', 'Environment', 'Department']
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    ec2_host_finder.do_set_key('Missing')
    assert mock_unique_tags.call_count == 1
    assert capsys.readouterr().out == 'Unknown value for tag key, it remains set to: Name\n'


@patch('ec2_ssh.EC2HostFinder.get_unique_instance_tag_keys')
def test_set_key_ec2_not_called(mock_unique_tags):
    """When the instance_tag_keys is populated it should not be updated by calling ec2"""
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    ec2_ssh.instance_tag_keys = ['Name', 'Environment', 'Department']
    ec2_host_finder.do_set_key('Environment')
    assert mock_unique_tags.call_count == 0


@patch('ec2_ssh.EC2HostFinder.get_unique_instance_tag_keys')
def test_set_key_complete_valid(mock_unique_tags):
    """Only the matching keys should be returned from the instance_tag_keys and should be sorted"""
    mock_unique_tags.return_value = ['Name', 'Environment', 'Environment2']
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    assert ec2_host_finder.complete_set_key('Env', None, None, None) == ['Environment', 'Environment2']
    assert mock_unique_tags.call_count == 1


@patch('ec2_ssh.EC2HostFinder.get_unique_instance_tag_keys')
def test_set_key_complete_no_match(mock_unique_tags):
    """An empty list should be returned with no match"""
    mock_unique_tags.return_value = ['Name', 'Environment', 'Environment2']
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    assert ec2_host_finder.complete_set_key('Missing', None, None, None) == []
    assert mock_unique_tags.call_count == 1


@patch('ec2_ssh.EC2HostFinder.get_unique_instance_tag_keys')
def test_set_key_complete_ec2_not_called(mock_unique_tags):
    """When the instance_tag_keys is populated it should not be updated by calling ec2 and matching items should
    be returned"""
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    ec2_ssh.instance_tag_keys = ['Name', 'Environment', 'Department']
    assert ec2_host_finder.complete_set_key('Env', None, None, None) == ['Environment']
    assert mock_unique_tags.call_count == 0
