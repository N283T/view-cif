"""Configuration management for view-cif."""

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


def _expand_path(value: str) -> str:
    """Expand ~ and environment variables in a path string."""
    if not value:
        return value
    return str(Path(os.path.expandvars(value)).expanduser())


CONFIG_DIR = Path.home().joinpath(".config", "view-cif")
CONFIG_FILE = CONFIG_DIR.joinpath("config.yaml")

DEFAULT_CACHE_DIR = Path.home().joinpath(".cache", "view-cif")


@dataclass(frozen=True)
class PathsConfig:
    pdb_next_gen: str = ""
    bird: str = ""
    monomers: str = ""
    chem_comp: str = ""
    prd: str = ""


@dataclass(frozen=True)
class Config:
    editor: str = "code"
    cache_dir: str = str(DEFAULT_CACHE_DIR)
    paths: PathsConfig = field(default_factory=PathsConfig)

    @property
    def cache_path(self) -> Path:
        return Path(self.cache_dir).expanduser()


def _config_from_dict(data: dict) -> Config:
    paths_data = data.get("paths", {})
    paths = PathsConfig(
        **{
            k: _expand_path(v)
            for k, v in paths_data.items()
            if k in PathsConfig.__dataclass_fields__
        }
    )
    return Config(
        editor=data.get("editor", "code"),
        cache_dir=data.get("cache_dir", str(DEFAULT_CACHE_DIR)),
        paths=paths,
    )


def _config_to_dict(config: Config) -> dict:
    return {
        "editor": config.editor,
        "cache_dir": config.cache_dir,
        "paths": {
            "pdb_next_gen": config.paths.pdb_next_gen,
            "bird": config.paths.bird,
            "monomers": config.paths.monomers,
            "chem_comp": config.paths.chem_comp,
            "prd": config.paths.prd,
        },
    }


def load_config(config_file: Path = CONFIG_FILE) -> Config:
    if not config_file.exists():
        config = Config()
        save_config(config, config_file)
        return config

    try:
        with open(config_file) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise SystemExit(
            f"Error: Config file {config_file} contains invalid YAML:\n{e}"
        ) from e
    except OSError as e:
        raise SystemExit(f"Error: Cannot read config file {config_file}: {e}") from e

    if data is None:
        return Config()

    return _config_from_dict(data)


VALID_TOP_KEYS = {"editor", "cache_dir"}
VALID_PATH_KEYS = set(PathsConfig.__dataclass_fields__)


def update_config(config: Config, key: str, value: str) -> Config:
    data = _config_to_dict(config)

    if "." in key:
        section, subkey = key.split(".", 1)
        if section != "paths" or subkey not in VALID_PATH_KEYS:
            valid = ", ".join(f"paths.{k}" for k in sorted(VALID_PATH_KEYS))
            raise SystemExit(f"Error: Unknown key '{key}'. Valid path keys: {valid}")
        return _config_from_dict({**data, "paths": {**data["paths"], subkey: value}})

    if key not in VALID_TOP_KEYS:
        valid = ", ".join(sorted(VALID_TOP_KEYS))
        raise SystemExit(
            f"Error: Unknown key '{key}'. Valid keys: {valid}, paths.<name>"
        )

    return _config_from_dict({**data, key: value})


def save_config(config: Config, config_file: Path = CONFIG_FILE) -> None:
    try:
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w") as f:
            yaml.dump(
                _config_to_dict(config), f, default_flow_style=False, sort_keys=False
            )
    except OSError as e:
        raise SystemExit(f"Error: Cannot write config file {config_file}: {e}") from e
