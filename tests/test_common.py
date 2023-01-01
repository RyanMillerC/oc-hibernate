"""Tests for hibernate.common functions."""

import json
from unittest.mock import patch

import pytest
from sh import ErrorReturnCode

from . import helper as test_helper
from hibernate import common, exceptions


@patch("hibernate.external.oc")
def test_get_aws_creds_from_ocp_exists(mocked):
    """Test common.get_aws_creds_from_ocp() when (mocked) OCP returns
    a secret."""
    def mock_oc(*args, **kwargs):
        response = test_helper.load_json_file(
            "./tests/mock_responses/minted_aws_creds_manifest.json"
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
        exception = ErrorReturnCode(full_cmd, stdout, stderr)
        raise exception
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
