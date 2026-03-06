# view-cif Rebuild Design

## Overview

CLI tool to read CIF files from various sources (file path, PDB code, CCD/PRD)
and display them in a configurable editor.

## Architecture

```
src/view_cif/
├── __init__.py      # Entry point (typer.run)
├── cli.py           # CLI definition and argument parsing
├── config.py        # Config file read/write (~/.config/view-cif/config.yaml)
├── resolver.py      # CIF source resolution (path/PDB code/CCD/PRD -> file path)
├── viewer.py        # Cache write + editor launch
```

## Config File

- Location: `~/.config/view-cif/config.yaml`
- Generated with defaults on first run

```yaml
editor: code
cache_dir: ~/.cache/view-cif

paths:
  pdb_next_gen: ""
  bird: ""
  monomers: ""
  chem_comp: ""
  prd: ""
```

## Cache

- Write CIF output to `~/.cache/view-cif/`
- Auto-delete files older than 7 days on startup
- Exit immediately after launching editor (no `--wait`)

## CLI Interface

```
view-cif <cont> [target_dir] [--ccd-definition/-d] [--next-gen/-n]
```

## Dependencies

- `gemmi` — CIF reading
- `typer` — CLI
- `pyyaml` — Config file

## Tests

- Unit tests for `resolver.py` source resolution logic
- Unit tests for `config.py` read/write

---
- [ ] **DONE** - Design complete
