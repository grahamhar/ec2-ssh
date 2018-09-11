import ec2_ssh
import pytest
from collections import defaultdict
from unittest.mock import patch


@pytest.fixture(autouse=True)
def reset_global_vars():
    ec2_ssh.instance_tag_value = 'Value'
    ec2_ssh.instance_key = 'Name'
    ec2_ssh.instance_tag_keys = []
    ec2_ssh.instance_tag_values = {}
    ec2_ssh.instance_ips = defaultdict(lambda: defaultdict(list))


@patch('ec2_ssh.EC2HostFinder.get_ec2_instances')
def test_ssh_complete_valid(mock_get_ec2_instances):
    """Only the matching IP Addresses should be returned from the instance_tag_keys and should be sorted"""
    mock_get_ec2_instances.return_value = ['1.1.1.1', '1.1.1.2', '2.1.1.1']
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    assert ec2_host_finder.complete_ssh('1', None, None, None) == ['1.1.1.1', '1.1.1.2']
    assert mock_get_ec2_instances.call_count == 1


@patch('ec2_ssh.EC2HostFinder.get_ec2_instances')
def test_ssh_complete_invalid(mock_get_ec2_instances):
    """with no matching IP Addresses should return an empty list"""
    mock_get_ec2_instances.return_value = ['1.1.1.1', '1.1.1.2', '2.1.1.1']
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    assert ec2_host_finder.complete_ssh('3', None, None, None) == []
    assert mock_get_ec2_instances.call_count == 1


@patch('ec2_ssh.EC2HostFinder.get_ec2_instances')
def test_ssh_complete_no_update(mock_get_ec2_instances):
    """when the instance list is already populated no call to ec2 should be made and
    only the matching IP Addresses should be returned from the instance_tag_keys and should be sorted"""
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    ec2_ssh.instance_ips = {'Name': {'Value': ['1.1.1.1', '1.1.1.2', '2.1.1.1']}}
    assert ec2_host_finder.complete_ssh('1', None, None, None) == ['1.1.1.1', '1.1.1.2']
    assert mock_get_ec2_instances.call_count == 0


def test_ssh_single_no_match(capsys):
    """When the value(IP) supplied to the ssh command is not known it should print the line"""
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    ec2_ssh.instance_ips = {'Name': {'Value': ['1.1.1.1']}}
    ec2_host_finder.do_ssh('2.2.2.2')
    assert capsys.readouterr().out == 'The supplied IP didn\'t match any EC2 instances tagged with Name:Value\n'


def test_ssh_no_ips_found(capsys):
    """The ssh command needs to have tab completion used first"""
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    ec2_host_finder.do_ssh('2.2.2.2')
    assert capsys.readouterr().out == 'Select either an IP address or a partial IP address using TAB complete\n\n'


@patch('ec2_ssh.EC2HostFinder.execute_ssh')
def test_ssh_single_ip_match(mock_ssh, capsys):
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    ec2_ssh.instance_ips = {'Name': {'Value': ['1.1.1.1', '2.2.2.2']}}
    ec2_host_finder.do_ssh('2.2.2.2')
    assert mock_ssh.call_count == 1
    assert capsys.readouterr().out == 'SSH to all hosts complete\n'

@patch('ec2_ssh.EC2HostFinder.execute_ssh')
def test_ssh_two_ip_match(mock_ssh, capsys):
    ec2_host_finder = ec2_ssh.EC2HostFinder()
    ec2_ssh.instance_ips = {'Name': {'Value': ['1.1.1.1', '2.2.2.2', '2.2.2.1']}}
    ec2_host_finder.do_ssh('2.2.2')
    assert capsys.readouterr().out == 'SSH to all hosts complete\n'
    assert mock_ssh.call_count == 2
