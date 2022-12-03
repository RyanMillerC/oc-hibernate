"""Helper functions for the hibernate package.
"""

import os
import sys

import sh


def get_resource_path(relative_path):
    """Get absolute path to resource. Works for dev and for PyInstaller.
    https://stackoverflow.com/a/31966932
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def run_preflight_checks():
    """Validate that prerequisites are installed."""

    # Validate Ansible is installed
    output = sh.ansible_playbook('--version')
    if output.exit_code != 0:
        print_error(
            'ERROR: "ansible_playbook" not found in $PATH.',
            'Install Ansible to use this plugin.'
        )
        sys.exit(1)

    # Validate AWS CLI is installed
    output = sh.aws('--version')
    if output.exit_code != 0:
        print_error(
            'ERROR: "aws" not found in $PATH.',
            'Install AWS CLI v2 to use this plugin.'
        )
        sys.exit(1)


def print_error(*args, **kwargs):
    """Works like print(), but prints to stderr instead of stdout."""
    print(*args, file=sys.stderr, **kwargs)
