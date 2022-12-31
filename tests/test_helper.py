"""Tests for hibernate.helper functions."""

import json
from unittest.mock import patch

import pytest

from . import helper as test_helper
from hibernate import helper


@patch("hibernate.helper.oc")
def test_get_aws_creds_from_ocp(mocked):
    def mock_oc(*args, **kwargs):
        response = test_helper.load_json_file(
            "./tests/mock_responses/minted_aws_creds_manifest.json"
        )
        return response
    mocked.side_effect = mock_oc

    response = helper.get_aws_creds_from_ocp()

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
