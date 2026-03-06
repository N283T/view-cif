"""CLI definition for view-cif."""

import typer
from typing_extensions import Annotated

from .config import (
    CONFIG_FILE,
    _config_to_dict,
    load_config,
    save_config,
    update_config,
)
from .resolver import resolve_cif
from .viewer import cleanup_old_cache, open_in_editor, write_cache

app = typer.Typer()
config_app = typer.Typer(help="Manage configuration")
app.add_typer(config_app, name="config")


@app.command()
def view(
    cont: Annotated[
        str, typer.Argument(help="CIF file path, PDB code, or compound name")
    ],
    target_dir: Annotated[
        str | None, typer.Argument(help="Directory to search for the CIF file")
    ] = None,
    ccd_def: Annotated[
        bool, typer.Option("--ccd-definition", "-d", help="CCD definition file type")
    ] = False,
    next_gen: Annotated[
        bool, typer.Option("--next-gen", "-n", help="Use pdb_next_gen file")
    ] = False,
):
    """View a CIF file in your editor."""
    try:
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
    except SystemExit:
        raise
    except Exception as e:
        raise SystemExit(f"Error: {e}") from e


@config_app.command("show")
def config_show():
    """Show current configuration."""
    config = load_config()
    data = _config_to_dict(config)
    typer.echo(f"Config file: {CONFIG_FILE}\n")
    for key, value in data.items():
        if isinstance(value, dict):
            typer.echo(f"{key}:")
            for k, v in value.items():
                display = v if v else "(not set)"
                typer.echo(f"  {k}: {display}")
        else:
            typer.echo(f"{key}: {value}")


@config_app.command("set")
def config_set(
    key: Annotated[
        str, typer.Argument(help="Config key (e.g., editor, paths.chem_comp)")
    ],
    value: Annotated[str, typer.Argument(help="Value to set")],
):
    """Set a configuration value."""
    config = load_config()
    new_config = update_config(config, key, value)
    save_config(new_config)
    typer.echo(f"Set {key} = {value}")
