"""Test helper functions."""

import json


def load_json_file(file_path):
    """Return a dictionary object loaded from a JSON file.

    Supports JSON files with comments as long as the line starts with "//" with
    any amount of leading spaces.
    """
    with open(file_path, "r") as stream:
        # Remove lines from JSON file starting with //
        json_removed_comments = ''.join(
            line for line in stream if not line.lstrip().startswith('//')
        )
        json_data = json.loads(json_removed_comments)
    return json_data
