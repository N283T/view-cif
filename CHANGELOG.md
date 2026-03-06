# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.2.0] - 2026-03-07

### Added

- `view-cif config show` command to display current configuration
- `view-cif config set <key> <value>` command to update config from CLI
- Configuration file at `~/.config/view-cif/config.yaml` (replaces environment variables)
- Configurable editor (default: `code`)
- Cache-based viewing in `~/.cache/view-cif/` with 7-day auto-cleanup
- Comprehensive error handling with user-friendly messages
- Validation of config paths before use
- Unit tests (39 tests, 79% coverage)

### Changed

- Rebuilt from single-file to modular architecture (`cli`, `config`, `resolver`, `viewer`)
- Replaced environment variables with YAML config file
- Replaced `--wait` blocking with fire-and-forget editor launch
- Migrated from `os.path` to `pathlib` with `joinpath()`

### Removed

- Environment variable configuration (`PDB_NEXT_GEN`, `BIRD`, `MONOMERS`, `CHEM_COMP`, `PRD_DIR`)
- `--wait` behavior (editor opens and CLI exits immediately)

## [0.1.0] - 2026-03-06

### Added

- Initial release
- View CIF files by file path, PDB code, or compound name
- PDB next-gen format support
- CCD and PRD/PRDCC bulk file support
