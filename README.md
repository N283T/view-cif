# view-cif

CLI tool to view CIF files from various sources in your preferred editor.

## Features

- Open CIF files by **file path**, **PDB code**, or **compound name**
- Automatic download from PDB (including next-gen format)
- CCD and PRD/PRDCC bulk file support
- Configurable editor and data paths via YAML config
- Cache-based viewing (no blocking `--wait`)

## Installation

Requires Python 3.12+.

```bash
uv tool install git+https://github.com/N283T/view_cif.git
```

## Usage

```bash
# Open a local CIF file
view-cif /path/to/structure.cif

# Open by PDB code (auto-downloads)
view-cif 1abc

# Open next-gen PDB format
view-cif 1abc --next-gen

# Open from a specific directory
view-cif ABC /path/to/cif/dir

# Open CCD chemical component
view-cif ATP

# Open PRD definition
view-cif prd --ccd-definition
```

### Options

| Option | Short | Description |
|:-------|:------|:------------|
| `--ccd-definition` | `-d` | Use CCD definition file type |
| `--next-gen` | `-n` | Use pdb_next_gen format |

## Configuration

On first run, a default config is created at `~/.config/view-cif/config.yaml`.

### Managing config via CLI

```bash
# Show current configuration
view-cif config show

# Change editor
view-cif config set editor nvim

# Set data paths
view-cif config set paths.chem_comp /data/chem_comp
view-cif config set paths.monomers /data/monomers
```

### Config keys

| Key | Description |
|:----|:------------|
| `editor` | Editor command to open CIF files (e.g., `code`, `nvim`, `emacs`) |
| `cache_dir` | Directory for cached CIF output |
| `paths.pdb_next_gen` | Root directory for next-gen PDB files |
| `paths.bird` | Root directory for BIRD (PRD) data |
| `paths.monomers` | Directory containing `components.cif.gz` |
| `paths.chem_comp` | Directory for chemical component CIF files |
| `paths.prd` | Directory for PRD definition CIF files |

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

MIT
