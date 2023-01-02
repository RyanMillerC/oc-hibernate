"""Tests for hibernate.common functions."""

import json
from unittest.mock import patch

import pytest
from _pytest.outcomes import Failed
from sh import ErrorReturnCode

from . import helper as test_helper
from hibernate import common, exceptions


@patch("hibernate.external.oc")
def test_get_aws_creds_from_ocp_exists(mocked):
    """Test common.get_aws_creds_from_ocp() when (mocked) OCP returns
    a secret."""
    def mock_oc(*args, **kwargs):
        response = test_helper.load_json_file(
            "./tests/mock_responses/oc/minted_aws_creds_manifest.json"
        )
        return response
    mocked.side_effect = mock_oc

    response = common.get_aws_creds_from_ocp()

    expected = {
        "access_key": "ACCESS_KEY",
        "secret_access_key": "SECRET_ACCESS_KEY"
    }
    assert response == expected

    mocked.assert_called_with(
        'get',
        'secret',
        'oc-hibernate',
        '--namespace', 'kube-system',
        '--output', 'json'
    )

@patch("hibernate.external.oc")
def test_get_aws_creds_from_ocp_does_not_exist(mocked):
    """Test common.get_aws_creds_from_ocp() when (mocked) OCP returns an
    error because the secret does not exist.

    The function should raise an OpenShiftNotFound error.
    """
    def mock_oc(*args, **kwargs):
        full_cmd = "oc get secret oc-hibernate --namespace kube-system --output json"
        stdout = b""
        stderr = b'Error from server (NotFound): secrets "oc-hibernate" not found\n'
        raise ErrorReturnCode(full_cmd, stdout, stderr)
    mocked.side_effect = mock_oc

    with pytest.raises(exceptions.OpenShiftNotFound):
        common.get_aws_creds_from_ocp()

    mocked.assert_called_with(
        'get',
        'secret',
        'oc-hibernate',
        '--namespace', 'kube-system',
        '--output', 'json'
    )


@patch("hibernate.external.aws")
def test_get_available_cluster_ids(mocked):
    """Test common.get_available_cluster_ids when (mocked) AWS returns a list
    of EC2 instances containing a single cluster."""
    def mock_aws(*args, **kwargs):
        response = None
        expected_args = (
            "ec2",
            "describe-instances",
            "--filter", f"Name=tag:Name,Values=*-master-0",
            "--output", "json",
            "--profile", "default"
        )
        if args == expected_args:
            response = test_helper.load_json_file(
                "./tests/mock_responses/aws/aws_get_master_0_with_single_cluster.json"
            )

        expected_args = (
            "ec2",
            "describe-instances",
            "--filter", 'Name=tag:Name,Values=ocp-m8cb9-*',
            "--output", "json",
            "--profile", "default"
        )
        if args == expected_args:
            response = test_helper.load_json_file(
                "./tests/mock_responses/aws/aws_get_ec2_instances_single_cluster.json"
            )

        if response:
            return response
        else:
            raise Failed(
                "Unknown arguments passed to (mock) external.aws\n"
                f"args: {args}\n"
                f"kwargs: {kwargs}"
            )
    mocked.side_effect = mock_aws

    # Profile name doesn't matter because the AWS "response" is mocked
    aws_profile_name = 'default'
    response = common.get_available_cluster_ids(aws_profile_name)

    expected = [
        {
            'cluster_id': 'ocp-m8cb9',
            'machines': [
                {
                    'name': 'ocp-m8cb9-worker-us-east-2a-rzkss',
                    'state': 'stopped'
                },
                {
                    'name': 'ocp-m8cb9-master-0',
                    'state': 'stopped'
                },
                {
                    'name': 'ocp-m8cb9-master-1',
                    'state': 'stopped'
                },
                {
                    'name': 'ocp-m8cb9-worker-us-east-2b-pkn6z',
                    'state': 'stopped'
                },
                {
                    'name': 'ocp-m8cb9-master-2',
                    'state': 'stopped'
                }
            ],
            'state': 'stopped'
        }
    ]

    assert response == expected
