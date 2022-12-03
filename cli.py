"""Entrypoint for oc-hibernate plugin. This exists so that pyinstaller has
a single module it can point at to build a binary from. The real plugin
code is in the ./hibernate directory.
"""

import sys

import hibernate.__main__ as main

if __name__ == '__main__':
    main.cli()
