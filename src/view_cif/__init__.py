"""view-cif: CLI tool to view CIF files from various sources."""

import sys

from .cli import app

SUBCOMMANDS = {"config", "--help", "--show-completion", "--install-completion"}


def main():
    if len(sys.argv) > 1 and sys.argv[1] not in SUBCOMMANDS:
        sys.argv.insert(1, "view")
    app()
