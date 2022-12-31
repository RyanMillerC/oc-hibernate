import json
from unittest.mock import patch

import pytest
from _pytest.outcomes import Failed
from click.testing import CliRunner

from . import helper
from hibernate.__main__ import fix_certs


@patch("hibernate.helper.oc")
def test_fix_certs(mocked):
    def mock_oc(*args, **kwargs):
        if args == ("get", "csr", "-o", "json"):
            response = helper.load_json_file("./tests/mock_responses/oc_pending_csr.json")
        elif args == ("adm", "certificate", "approve", "csr-4t9vw", "csr-76sjh") \
            and kwargs == {'stream': True}:
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
    mocked.side_effect = mock_oc

    runner = CliRunner()
    result = runner.invoke(fix_certs)
    assert result.exit_code == 0

    mocked.assert_any_call('get', 'csr', '-o', 'json')
    mocked.assert_any_call('adm', 'certificate', 'approve', 'csr-4t9vw', 'csr-76sjh', stream=True)
