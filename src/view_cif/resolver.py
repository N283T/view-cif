"""Resolve CIF source identifiers to file content."""

from pathlib import Path

from gemmi import expand_if_pdb_code, is_pdb_code
from gemmi.cif import read as read_cif

from .config import PathsConfig


def _require_path(value: str, name: str) -> None:
    if not value:
        raise SystemExit(
            f"Error: '{name}' path not configured. "
            f"Set paths.{name} in ~/.config/view-cif/config.yaml"
        )


def _safe_read_cif(path: str) -> str:
    try:
        return read_cif(path).as_string()
    except FileNotFoundError:
        raise SystemExit(f"Error: CIF file not found: {path}")
    except (RuntimeError, OSError) as e:
        raise SystemExit(f"Error: Failed to read CIF file '{path}': {e}")


def _find_cif_file(name: str, directory: str) -> Path:
    dir_path = Path(directory)
    # Flat: {dir}/{name}.cif
    for ext in (".cif", ".cif.gz"):
        candidate = dir_path.joinpath(name + ext)
        if candidate.exists():
            return candidate
    # Nested: {dir}/**/{name}/{name}.cif (PDB mirror structure)
    matches = list(dir_path.glob(f"**/{name}/{name}.cif"))
    if matches:
        return matches[0]
    matches = list(dir_path.glob(f"**/{name}.cif"))
    if matches:
        return matches[0]
    raise SystemExit(f"Error: File {name}.cif not found in {directory}")


def _resolve_file_path(cont: str) -> str:
    return _safe_read_cif(cont)


def _resolve_target_dir(cont: str, target_dir: str) -> str:
    path = _find_cif_file(cont, target_dir)
    return _safe_read_cif(str(path))


def _resolve_pdb_code(cont: str, next_gen: bool, paths: PathsConfig) -> tuple[str, str]:
    """Resolve a PDB code. Returns (content, suggested_filename)."""
    if next_gen:
        _require_path(paths.pdb_next_gen, "pdb_next_gen")
        next_gen_id = "pdb_" + cont.zfill(8)
        path = Path(paths.pdb_next_gen).joinpath(
            "entries",
            "divided",
            cont[1:3],
            next_gen_id,
            next_gen_id + "_xyz-enrich.cif.gz",
        )
        content = _safe_read_cif(str(path))
        return content, next_gen_id + "_xyz-enrich.cif"

    content = _safe_read_cif(expand_if_pdb_code(cont))
    return content, cont + ".cif"


def _resolve_prd(ccd_def: bool, paths: PathsConfig) -> str:
    _require_path(paths.bird, "bird")
    prd_dir = Path(paths.bird)
    if ccd_def:
        return _safe_read_cif(str(prd_dir.joinpath("prd-all.cif.gz")))
    return _safe_read_cif(str(prd_dir.joinpath("prdcc-all.cif.gz")))


def _resolve_ccd(paths: PathsConfig) -> str:
    _require_path(paths.monomers, "monomers")
    return _safe_read_cif(str(Path(paths.monomers).joinpath("components.cif.gz")))


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
    cont_path = Path(cont)
    if cont_path.exists():
        if not cont_path.is_file():
            raise SystemExit(f"Error: '{cont}' is not a file.")
        return _resolve_file_path(cont), cont_path.stem + ".cif"

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
        _require_path(paths.prd, "prd")
        path = _find_cif_file(cont.upper(), paths.prd)
        return _safe_read_cif(str(path)), default_filename

    _require_path(paths.chem_comp, "chem_comp")
    path = _find_cif_file(cont.upper(), paths.chem_comp)
    return _safe_read_cif(str(path)), default_filename
