"""view-cif: CLI tool to view CIF files from various sources."""

import typer

from .cli import view_cif


def main():
    typer.run(view_cif)
