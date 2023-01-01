"""Functions for making calls to external programs.

All external calls are made through the `sh` module.

Calling external programs for Kubernetes (OpenShift) and AWS removes the need
to include their SDKs/API libraries in the oc-hibernate binary.
"""

import json
import sys

import sh

from hibernate import helper


def oc(*args, stream=False, **kwargs):
    """Run `oc` external command. If stream is True, output of the command
    will be streamed to stdout instead of returned. If stream is False, the
    output from the command will be returned as a dictionary.

    The command being called MUST return valid JSON if stream if False!

    This function will handle errors.
    """
    if stream:
        response = _external_cmd_stream_output('oc', *args, **kwargs)
    else:
        response = _external_cmd_json_output('oc', *args, **kwargs)
    return response


def _external_cmd_json_output(cmd, *args, **kwargs):
    """Call an external command that returns JSON in a subshell and return a
    dictionary loaded from stdout.

    The command being called MUST return valid JSON. This function will handle
    errors.

    :param str cmd:
        Name or path of command to run
    :param *args:
        Optional positional arguments to pass when running the command
    :param **kwargs:
        Optional keyword arguments passed to sh.Command instance
    """
    try:
        command = sh.Command(cmd)
        cmd_output = command(*args, **kwargs)
        response = json.loads(cmd_output.stdout)
    except sh.ErrorReturnCode as exception:
        print(exception.stdout.decode('utf-8'), end="")
        helper.print_error(exception.stderr.decode('utf-8'), end="")
        raise exception
    except Exception as exception:
        # TODO: yeah...
        print("OH NO!")
        raise exception
    return response


def _external_cmd_stream_output(cmd, *args, **kwargs):
    """Call an external command in a subshell and stream the output to
    stdout and stderr.

    :param str cmd:
        Name or path of command to run
    :param *args:
        Optional positional arguments to pass when running the command
    :param **kwargs:
        Optional keyword arguments passed to sh.Command instance
    """
    command = sh.Command(cmd)
    return command(*args, _in=sys.stdin, _out=sys.stdout, **kwargs)
