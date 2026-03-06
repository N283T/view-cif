"""Resolve CIF source identifiers to file content."""

from pathlib import Path

from gemmi import expand_if_pdb_code, is_pdb_code
from gemmi.cif import read as read_cif

from .config import PathsConfig


def _find_cif_file(name: str, directory: str) -> Path:
    dir_path = Path(directory)
    for ext in (".cif", ".cif.gz"):
        candidate = dir_path.joinpath(name + ext)
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"File {name}.cif not found in {directory}")


def _resolve_file_path(cont: str) -> str:
    return read_cif(cont).as_string()


def _resolve_target_dir(cont: str, target_dir: str) -> str:
    path = _find_cif_file(cont, target_dir)
    return read_cif(str(path)).as_string()


def _resolve_pdb_code(cont: str, next_gen: bool, paths: PathsConfig) -> tuple[str, str]:
    """Resolve a PDB code. Returns (content, suggested_filename)."""
    if next_gen:
        next_gen_id = "pdb_" + cont.zfill(8)
        path = Path(paths.pdb_next_gen).joinpath(
            "data", "entries", "divided",
            cont[1:3],
            next_gen_id,
            next_gen_id + "_xyz-enrich.cif.gz",
        )
        content = read_cif(str(path)).as_string()
        return content, next_gen_id + "_xyz-enrich.cif"

    content = read_cif(expand_if_pdb_code(cont)).as_string()
    return content, cont + ".cif"


def _resolve_prd(ccd_def: bool, paths: PathsConfig) -> str:
    prd_dir = Path(paths.bird).joinpath("prd")
    if ccd_def:
        return read_cif(str(prd_dir.joinpath("prd-all.cif.gz"))).as_string()
    return read_cif(str(prd_dir.joinpath("prdcc-all.cif.gz"))).as_string()


def _resolve_ccd(paths: PathsConfig) -> str:
    return read_cif(str(Path(paths.monomers).joinpath("components.cif.gz"))).as_string()


def resolve_cif(
    cont: str,
    paths: PathsConfig,
    *,
    target_dir: str | None = None,
    ccd_def: bool = False,
    next_gen: bool = False,
) -> tuple[str, str]:
    """Resolve a CIF identifier to (content, output_filename).

    Returns:
        Tuple of (cif_content_string, suggested_output_filename).
    """
    default_filename = cont + ".cif"

    # Direct file path
    if Path(cont).exists():
        return _resolve_file_path(cont), Path(cont).stem + ".cif"

    # Explicit target directory
    if target_dir:
        return _resolve_target_dir(cont, target_dir), default_filename

    # PDB code
    if is_pdb_code(cont):
        return _resolve_pdb_code(cont, next_gen, paths)

    # PRD or CCD bulk files
    if cont.lower() == "prd":
        return _resolve_prd(ccd_def, paths), "prd.cif"

    if cont.lower() == "ccd":
        return _resolve_ccd(paths), "ccd.cif"

    # CCD definition or chemical component lookup
    if ccd_def:
        path = _find_cif_file(cont.upper(), paths.prd)
        return read_cif(str(path)).as_string(), default_filename

    path = _find_cif_file(cont.upper(), paths.chem_comp)
    return read_cif(str(path)).as_string(), default_filename
