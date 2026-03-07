# view-cif

[![PyPI](https://img.shields.io/pypi/v/view-cif)](https://pypi.org/project/view-cif/)
[![Python](https://img.shields.io/pypi/pyversions/view-cif)](https://pypi.org/project/view-cif/)
[![Test](https://github.com/N283T/view-cif/actions/workflows/test.yml/badge.svg)](https://github.com/N283T/view-cif/actions/workflows/test.yml)
[![License](https://img.shields.io/github/license/N283T/view-cif)](LICENSE)

CLI tool to view CIF files from various sources in your preferred editor.

## Features

- Open CIF files by **file path**, **PDB code**, or **compound name**
- Automatic download from PDB (including next-gen format)
- **BIRD individual lookup** — auto-detects `PRD_`, `PRDCC_`, `FAM_` prefixes
- CCD and PRD/PRDCC bulk file support
- Configurable editor and data paths via YAML config
- Cache-based viewing (no blocking `--wait`)

## Installation

Requires Python 3.12+.

```bash
# From PyPI
pip install view-cif

# Or with uv
uv tool install view-cif
```

## Usage

```bash
# Open a local CIF file
view-cif /path/to/structure.cif

# Open by PDB code (uses local mirror or auto-downloads)
view-cif 1abc

# Open next-gen PDB format
view-cif 1abc --next-gen

# Open from a specific directory
view-cif ABC /path/to/cif/dir

# Open CCD chemical component
view-cif ATP

# Individual BIRD lookups (auto-detected by prefix)
view-cif PRD_000010      # PRD definition
view-cif PRDCC_000240    # PRD chemical component
view-cif FAM_000160      # PRD family

# Bulk files
view-cif prd             # prd-all.cif.gz
view-cif prdcc           # prdcc-all.cif.gz
view-cif ccd             # components.cif.gz
```

### Options

| Option | Short | Description |
|:-------|:------|:------------|
| `--next-gen` | `-n` | Use pdb_next_gen format |

## Configuration

On first run, a default config is created at `~/.config/view-cif/config.yaml`.
See [`config.example.yaml`](config.example.yaml) for a fully commented template.

### Managing config via CLI

```bash
# Show current configuration
view-cif config show

# Change editor
view-cif config set editor nvim

# Set data paths
view-cif config set paths.chem_comp /data/chem_comp
view-cif config set paths.prd /data/bird
```

### Config keys

| Key | Description | Example |
|:----|:------------|:--------|
| `editor` | Editor command (any terminal command) | `code`, `nvim`, `vim` |
| `cache_dir` | Directory for cached CIF output | `~/.cache/view-cif` |
| `paths.pdb_next_gen` | Next-gen PDB archive root | `/data/pdb_nextgen` |
| `paths.bird` | BIRD bulk files (`prd-all.cif.gz`, `prdcc-all.cif.gz`) | `/data/bird/prd` |
| `paths.monomers` | CCD monomers (`components.cif.gz`) | `/data/monomers` |
| `paths.chem_comp` | Chemical component reference data | `/data/chem_comp` |
| `paths.prd` | BIRD reference root (`prd/`, `prdcc/`, `family/` subdirs) | `/data/refdata/bird` |

### Directory structure expectations

Path resolution follows the [PDB FTP/rsync mirror](https://www.wwpdb.org/ftp/pdb-ftp-sites) directory layout.
If you maintain a local mirror, point each config path to the corresponding directory.

`~` and environment variables (`$HOME`, `$PDB_ROOT`, etc.) are expanded automatically.

```
paths.pdb_next_gen/
  entries/divided/{ab}/pdb_{id}/pdb_{id}_xyz-enrich.cif.gz

paths.bird/
  prd-all.cif.gz
  prdcc-all.cif.gz

paths.monomers/
  components.cif.gz

paths.chem_comp/
  {X}/{ABC}/ABC.cif          # nested by first character

paths.prd/
  prd/    {N}/PRD_NNNNNN.cif
  prdcc/  {N}/PRDCC_NNNNNN.cif
  family/ {N}/FAM_NNNNNN.cif
```

## Development

```bash
# Install with dev dependencies
uv sync --group dev

# Run tests
uv run pytest --cov=view_cif -v

# Lint
uv run ruff check .
```

## License

[MIT](LICENSE)
