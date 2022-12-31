"""Test helper functions."""

import json


def load_json_file(file_path):
    """Return a dictionary object loaded from a JSON file."""
    with open(file_path, "r") as stream:
        json_data = json.load(stream)
    return json_data
