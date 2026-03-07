# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.2.3] - 2026-03-07

### Added

- BIRD individual file lookup with prefix auto-detection (`PRD_`, `PRDCC_`, `FAM_`)
- Separate `view-cif prd` and `view-cif prdcc` bulk commands
- Support for `~` and environment variables (`$HOME`, etc.) in config paths
- `config.example.yaml` template with comments

### Changed

- CI optimized: skip docs-only changes, reduce matrix for PR/push (full matrix on release)

### Removed

- `--ccd-definition` / `-d` flag (replaced by prefix auto-detection)

## [0.2.2] - 2026-03-07

### Fixed

- Replace `typing_extensions.Annotated` with `typing.Annotated` (stdlib in Python 3.12+)

## [0.2.1] - 2026-03-07

### Added

- `view-cif config show` and `view-cif config set` CLI commands
- CI test matrix (Python 3.12/3.13/3.14 × ubuntu/macos)
- Auto-generated GitHub Releases from CHANGELOG
- README badges (PyPI, Python versions, test status, license)
- MIT LICENSE file
- Python 3.13/3.14 support

### Changed

- `view-cif <arg>` shorthand preserved alongside subcommands

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
