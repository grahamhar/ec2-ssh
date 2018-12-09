import os

from unittest.mock import patch, Mock

import pytest

from click import UsageError
from ec2_ssh import ec2_helpers

@pytest.fixture(autouse=True)
def setup():
    try:
        del os.environ['AWS_PROFILE']
    except KeyError:
        pass
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = '/does/not/exist'
    ec2_helpers.boto3_session = Mock()
    ec2_helpers.current_aws_profile = None
    ec2_helpers.ec2_client = None


def test_with_no_aws_profile():
    """With no or an incorrectly configured AWS_PROFILE or the default profile missing it should raise the correct exception"""
    with pytest.raises(UsageError) as exception_raised:
        ec2_helpers.get_ec2_client()


# @patch('ec2_ssh.ec2_helpers.get_region')
# @patch('ec2_ssh.ec2_helpers.get_aws_session')
# @patch('ec2_ssh.ec2_helpers.boto3')
# def test_changed_aws_profile(mock_get_region, mock_get_aws_session, mock_boto3):
#     """When the AWS_PROFILE is changed it should create new boto3 session"""
#     os.environ['AWS_PROFILE'] = 'fake_profile_ec2_testing'
#     ec2_helpers.boto3_session = Mock().get_credentials.return_value = Mock()
#     print(ec2_helpers.boto3_session)
#     assert ec2_helpers.get_ec2_client() is None
#     assert 1 == mock_get_aws_session.call.call_count
