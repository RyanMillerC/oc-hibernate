import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from hibernate.__main__ import fix_certs


def load_json_file(file_path):
    """Return a dictionary object loaded from a JSON file."""
    with open(file_path, "r") as stream:
        json_data = json.load(stream)
    return json_data


def mock_oc(*args, **kwargs):
    if args == ("get", "csr", "-o", "json"):
        response = load_json_file("./tests/mock_responses/oc_pending_csr.json")

    elif args == ('adm', 'certificate', 'approve', 'csr-4t9vw', 'csr-76sjh'):
        # TODO: This isn't actually doing anything because the output is being
        # written to stdout directly instead of returned by helper.oc
        response = "ok"

    else:
        print("Unknown arguments passed to (mock) helper.oc")
        assert False

    return response


@patch("hibernate.helper.oc", mock_oc)
def test_fix_certs():
    runner = CliRunner()
    result = runner.invoke(fix_certs)
    assert result.exit_code == 0
    # TODO: Should probably figure out a way to test
