"""Tests for resolver module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from view_cif.config import PathsConfig
from view_cif.resolver import _find_cif_file, resolve_cif

import pytest


class TestFindCifFile:
    def test_finds_cif(self, tmp_path: Path):
        cif_file = tmp_path.joinpath("ABC.cif")
        cif_file.write_text("data_ABC")
        result = _find_cif_file("ABC", str(tmp_path))
        assert result == cif_file

    def test_finds_cif_gz(self, tmp_path: Path):
        gz_file = tmp_path.joinpath("ABC.cif.gz")
        gz_file.write_text("dummy")  # Not real gz, just for path resolution
        result = _find_cif_file("ABC", str(tmp_path))
        assert result == gz_file

    def test_raises_on_missing(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError, match="ABC.cif not found"):
            _find_cif_file("ABC", str(tmp_path))


class TestResolveCif:
    @patch("view_cif.resolver.read_cif")
    def test_resolve_file_path(self, mock_read_cif, tmp_path: Path):
        cif_file = tmp_path.joinpath("test.cif")
        cif_file.write_text("data_test")

        mock_doc = MagicMock()
        mock_doc.as_string.return_value = "data_test"
        mock_read_cif.return_value = mock_doc

        paths = PathsConfig()
        content, filename = resolve_cif(str(cif_file), paths)

        assert content == "data_test"
        assert filename == "test.cif"

    @patch("view_cif.resolver.read_cif")
    def test_resolve_with_target_dir(self, mock_read_cif, tmp_path: Path):
        cif_file = tmp_path.joinpath("ABC.cif")
        cif_file.write_text("data_ABC")

        mock_doc = MagicMock()
        mock_doc.as_string.return_value = "data_ABC"
        mock_read_cif.return_value = mock_doc

        paths = PathsConfig()
        content, filename = resolve_cif("ABC", paths, target_dir=str(tmp_path))

        assert content == "data_ABC"
        assert filename == "ABC.cif"

    @patch("view_cif.resolver.read_cif")
    @patch("view_cif.resolver.expand_if_pdb_code")
    @patch("view_cif.resolver.is_pdb_code", return_value=True)
    def test_resolve_pdb_code(self, mock_is_pdb, mock_expand, mock_read_cif):
        mock_expand.return_value = "/some/path.cif"
        mock_doc = MagicMock()
        mock_doc.as_string.return_value = "data_1abc"
        mock_read_cif.return_value = mock_doc

        paths = PathsConfig()
        content, filename = resolve_cif("1abc", paths)

        assert content == "data_1abc"
        assert filename == "1abc.cif"
        mock_expand.assert_called_once_with("1abc")
