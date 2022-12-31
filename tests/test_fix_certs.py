import json
from unittest.mock import patch

import pytest
from _pytest.outcomes import Failed
from click.testing import CliRunner

from . import helper
from hibernate.__main__ import fix_certs


def mock_external_cmd_json_output(*args, **kwargs):
    if args == ("oc", "get", "csr", "-o", "json"):
        response = helper.load_json_file("./tests/mock_responses/oc_pending_csr.json")
    else:
        raise Failed(
            "Unknown arguments passed to (mock) helper.oc\n"
            f"args: {args}\n"
            f"kwargs: {kwargs}"
        )
    return response

def mock_external_cmd_stream_output(*args, **kwargs):
    if args == ("oc", "adm", "certificate", "approve", "csr-4t9vw", "csr-76sjh"):
        # oc prints directly to stdout. As long as this mock got proper input,
        # no output needs to be tested.
        return
    else:
        raise Failed(
            "Unknown arguments passed to (mock) helper.oc\n"
            f"args: {args}\n"
            f"kwargs: {kwargs}"
        )
    return response


@patch("hibernate.helper.external_cmd_json_output", mock_external_cmd_json_output)
@patch("hibernate.helper.external_cmd_stream_output", mock_external_cmd_stream_output)
def test_fix_certs(capsys):
    runner = CliRunner()
    result = runner.invoke(fix_certs)
    assert result.exit_code == 0
