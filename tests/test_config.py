"""Tests for config module."""

from pathlib import Path

import yaml

import pytest

from view_cif.config import (
    Config,
    PathsConfig,
    _config_from_dict,
    _config_to_dict,
    _expand_path,
    load_config,
    save_config,
    update_config,
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


class TestUpdateConfig:
    def test_update_top_level_key(self):
        config = Config()
        updated = update_config(config, "editor", "nvim")
        assert updated.editor == "nvim"
        assert updated.cache_dir == config.cache_dir

    def test_update_path_key(self):
        config = Config()
        updated = update_config(config, "paths.chem_comp", "/data/chem_comp")
        assert updated.paths.chem_comp == "/data/chem_comp"
        assert updated.editor == config.editor

    def test_rejects_unknown_top_key(self):
        with pytest.raises(SystemExit, match="Unknown key 'bogus'"):
            update_config(Config(), "bogus", "value")

    def test_rejects_unknown_path_key(self):
        with pytest.raises(SystemExit, match="Unknown key 'paths.bogus'"):
            update_config(Config(), "paths.bogus", "value")

    def test_rejects_invalid_section(self):
        with pytest.raises(SystemExit, match="Unknown key 'foo.bar'"):
            update_config(Config(), "foo.bar", "value")


class TestExpandPath:
    def test_empty_string_unchanged(self):
        assert _expand_path("") == ""

    def test_absolute_path_unchanged(self):
        assert _expand_path("/data/pdb") == "/data/pdb"

    def test_tilde_expanded(self):
        result = _expand_path("~/pdb/data")
        assert not result.startswith("~")
        assert result.endswith("/pdb/data")

    def test_env_var_expanded(self, monkeypatch):
        monkeypatch.setenv("MY_DATA", "/opt/data")
        assert _expand_path("$MY_DATA/pdb") == "/opt/data/pdb"

    def test_tilde_and_env_var_combined(self, monkeypatch):
        monkeypatch.setenv("SUBDIR", "pdb")
        result = _expand_path("~/$SUBDIR/data")
        assert not result.startswith("~")
        assert result.endswith("/pdb/data")


class TestConfigFromDictPathExpansion:
    def test_paths_expand_tilde(self):
        data = {"paths": {"bird": "~/pdb/bird"}}
        config = _config_from_dict(data)
        assert not config.paths.bird.startswith("~")
        assert config.paths.bird.endswith("/pdb/bird")

    def test_paths_expand_env_var(self, monkeypatch):
        monkeypatch.setenv("PDB_ROOT", "/data/pdb")
        data = {"paths": {"monomers": "$PDB_ROOT/monomers"}}
        config = _config_from_dict(data)
        assert config.paths.monomers == "/data/pdb/monomers"
