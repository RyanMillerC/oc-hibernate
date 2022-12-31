"""Test helper functions."""

import json


def load_json_file(file_path):
    """Return a dictionary object loaded from a JSON file."""
    with open(file_path, "r") as stream:
        # Remove lines from JSON file starting with //
        json_removed_comments = ''.join(
            line for line in stream if not line.startswith('//')
        )
        json_data = json.loads(json_removed_comments)
    return json_data
