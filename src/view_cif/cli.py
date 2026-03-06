"""CLI definition for view-cif."""

import typer
from typing_extensions import Annotated

from .config import load_config
from .resolver import resolve_cif
from .viewer import cleanup_old_cache, open_in_editor, write_cache


def view_cif(
    cont: Annotated[str, typer.Argument(help="CIF file path, PDB code, or compound name")],
    target_dir: Annotated[str | None, typer.Argument(help="Directory to search for the CIF file")] = None,
    ccd_def: Annotated[bool, typer.Option("--ccd-definition", "-d", help="CCD definition file type")] = False,
    next_gen: Annotated[bool, typer.Option("--next-gen", "-n", help="Use pdb_next_gen file")] = False,
):
    config = load_config()

    cleanup_old_cache(config.cache_path)

    content, filename = resolve_cif(
        cont,
        config.paths,
        target_dir=target_dir,
        ccd_def=ccd_def,
        next_gen=next_gen,
    )

    output = write_cache(content, filename, config.cache_path)
    open_in_editor(output, config.editor)
