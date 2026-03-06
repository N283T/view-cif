"""Tests for config module."""

from pathlib import Path

import yaml

from view_cif.config import (
    Config,
    PathsConfig,
    _config_from_dict,
    _config_to_dict,
    load_config,
    save_config,
)


class TestConfigFromDict:
    def test_empty_dict_returns_defaults(self):
        config = _config_from_dict({})
        assert config.editor == "code"
        assert config.paths.pdb_next_gen == ""

    def test_full_dict(self):
        data = {
            "editor": "vim",
            "cache_dir": "/tmp/test-cache",
            "paths": {
                "pdb_next_gen": "/data/pdb",
                "bird": "/data/bird",
                "monomers": "/data/monomers",
                "chem_comp": "/data/chem_comp",
                "prd": "/data/prd",
            },
        }
        config = _config_from_dict(data)
        assert config.editor == "vim"
        assert config.cache_dir == "/tmp/test-cache"
        assert config.paths.pdb_next_gen == "/data/pdb"
        assert config.paths.bird == "/data/bird"

    def test_ignores_unknown_path_keys(self):
        data = {"paths": {"unknown_key": "/some/path", "bird": "/data/bird"}}
        config = _config_from_dict(data)
        assert config.paths.bird == "/data/bird"


class TestConfigToDict:
    def test_roundtrip(self):
        config = Config(
            editor="vim",
            cache_dir="/tmp/cache",
            paths=PathsConfig(bird="/data/bird"),
        )
        data = _config_to_dict(config)
        restored = _config_from_dict(data)
        assert restored == config


class TestLoadSaveConfig:
    def test_load_creates_default_if_missing(self, tmp_path: Path):
        config_file = tmp_path.joinpath("config.yaml")
        config = load_config(config_file)
        assert config.editor == "code"
        assert config_file.exists()

    def test_save_and_load_roundtrip(self, tmp_path: Path):
        config_file = tmp_path.joinpath("config.yaml")
        original = Config(
            editor="emacs",
            cache_dir="/tmp/my-cache",
            paths=PathsConfig(monomers="/data/monomers"),
        )
        save_config(original, config_file)
        loaded = load_config(config_file)
        assert loaded == original

    def test_load_partial_config(self, tmp_path: Path):
        config_file = tmp_path.joinpath("config.yaml")
        config_file.write_text(yaml.dump({"editor": "nano"}))
        config = load_config(config_file)
        assert config.editor == "nano"
        assert config.paths.pdb_next_gen == ""
