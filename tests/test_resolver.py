"""Tests for resolver module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from view_cif.config import PathsConfig
from view_cif.resolver import _find_cif_file, _require_path, resolve_cif


class TestRequirePath:
    def test_passes_with_value(self):
        _require_path("/some/path", "test")

    def test_raises_on_empty(self):
        with pytest.raises(SystemExit, match="'test' path not configured"):
            _require_path("", "test")


class TestFindCifFile:
    def test_finds_cif(self, tmp_path: Path):
        cif_file = tmp_path.joinpath("ABC.cif")
        cif_file.write_text("data_ABC")
        result = _find_cif_file("ABC", str(tmp_path))
        assert result == cif_file

    def test_finds_cif_gz(self, tmp_path: Path):
        gz_file = tmp_path.joinpath("ABC.cif.gz")
        gz_file.write_text("dummy")
        result = _find_cif_file("ABC", str(tmp_path))
        assert result == gz_file

    def test_raises_on_missing(self, tmp_path: Path):
        with pytest.raises(SystemExit, match="ABC.cif not found"):
            _find_cif_file("ABC", str(tmp_path))


class TestResolveCif:
    @patch("view_cif.resolver._safe_read_cif")
    def test_resolve_file_path(self, mock_read, tmp_path: Path):
        cif_file = tmp_path.joinpath("test.cif")
        cif_file.write_text("data_test")

        mock_read.return_value = "data_test"

        paths = PathsConfig()
        content, filename = resolve_cif(str(cif_file), paths)

        assert content == "data_test"
        assert filename == "test.cif"

    def test_resolve_directory_raises(self, tmp_path: Path):
        with pytest.raises(SystemExit, match="is not a file"):
            resolve_cif(str(tmp_path), PathsConfig())

    @patch("view_cif.resolver._safe_read_cif")
    def test_resolve_with_target_dir(self, mock_read, tmp_path: Path):
        cif_file = tmp_path.joinpath("ABC.cif")
        cif_file.write_text("data_ABC")

        mock_read.return_value = "data_ABC"

        paths = PathsConfig()
        content, filename = resolve_cif("ABC", paths, target_dir=str(tmp_path))

        assert content == "data_ABC"
        assert filename == "ABC.cif"

    @patch("view_cif.resolver._safe_read_cif")
    @patch("view_cif.resolver.expand_if_pdb_code")
    @patch("view_cif.resolver.is_pdb_code", return_value=True)
    def test_resolve_pdb_code(self, mock_is_pdb, mock_expand, mock_read):
        mock_expand.return_value = "/some/path.cif"
        mock_read.return_value = "data_1abc"

        paths = PathsConfig()
        content, filename = resolve_cif("1abc", paths)

        assert content == "data_1abc"
        assert filename == "1abc.cif"
        mock_expand.assert_called_once_with("1abc")

    @patch("view_cif.resolver._safe_read_cif")
    @patch("view_cif.resolver.is_pdb_code", return_value=True)
    def test_resolve_pdb_code_next_gen(self, mock_is_pdb, mock_read):
        mock_read.return_value = "data_next_gen"

        paths = PathsConfig(pdb_next_gen="/data/pdb")
        content, filename = resolve_cif("1abc", paths, next_gen=True)

        assert content == "data_next_gen"
        assert filename == "pdb_00001abc_xyz-enrich.cif"
        mock_read.assert_called_once_with(
            str(
                Path("/data/pdb").joinpath(
                    "data", "entries", "divided", "ab",
                    "pdb_00001abc", "pdb_00001abc_xyz-enrich.cif.gz",
                )
            )
        )

    @patch("view_cif.resolver.is_pdb_code", return_value=True)
    def test_resolve_pdb_code_next_gen_missing_path(self, mock_is_pdb):
        paths = PathsConfig()
        with pytest.raises(SystemExit, match="pdb_next_gen"):
            resolve_cif("1abc", paths, next_gen=True)

    @patch("view_cif.resolver._safe_read_cif")
    @patch("view_cif.resolver.is_pdb_code", return_value=False)
    def test_resolve_prd(self, mock_is_pdb, mock_read):
        mock_read.return_value = "prdcc_data"

        paths = PathsConfig(bird="/data/bird")
        content, filename = resolve_cif("prd", paths)

        assert content == "prdcc_data"
        assert filename == "prd.cif"
        mock_read.assert_called_once_with(
            str(Path("/data/bird").joinpath("prd", "prdcc-all.cif.gz"))
        )

    @patch("view_cif.resolver._safe_read_cif")
    @patch("view_cif.resolver.is_pdb_code", return_value=False)
    def test_resolve_prd_ccd_def(self, mock_is_pdb, mock_read):
        mock_read.return_value = "prd_data"

        paths = PathsConfig(bird="/data/bird")
        content, filename = resolve_cif("prd", paths, ccd_def=True)

        assert content == "prd_data"
        assert filename == "prd.cif"
        mock_read.assert_called_once_with(
            str(Path("/data/bird").joinpath("prd", "prd-all.cif.gz"))
        )

    @patch("view_cif.resolver._safe_read_cif")
    @patch("view_cif.resolver.is_pdb_code", return_value=False)
    def test_resolve_ccd(self, mock_is_pdb, mock_read):
        mock_read.return_value = "ccd_data"

        paths = PathsConfig(monomers="/data/monomers")
        content, filename = resolve_cif("ccd", paths)

        assert content == "ccd_data"
        assert filename == "ccd.cif"
        mock_read.assert_called_once_with(
            str(Path("/data/monomers").joinpath("components.cif.gz"))
        )

    @patch("view_cif.resolver.is_pdb_code", return_value=False)
    def test_resolve_prd_missing_path(self, mock_is_pdb):
        with pytest.raises(SystemExit, match="bird"):
            resolve_cif("prd", PathsConfig())

    @patch("view_cif.resolver._safe_read_cif")
    @patch("view_cif.resolver.is_pdb_code", return_value=False)
    def test_resolve_chem_comp_lookup(self, mock_is_pdb, mock_read, tmp_path: Path):
        cif_file = tmp_path.joinpath("ATP.cif")
        cif_file.write_text("data_ATP")
        mock_read.return_value = "data_ATP"

        paths = PathsConfig(chem_comp=str(tmp_path))
        content, filename = resolve_cif("atp", paths)

        assert content == "data_ATP"
        assert filename == "atp.cif"

    @patch("view_cif.resolver._safe_read_cif")
    @patch("view_cif.resolver.is_pdb_code", return_value=False)
    def test_resolve_ccd_def_lookup(self, mock_is_pdb, mock_read, tmp_path: Path):
        cif_file = tmp_path.joinpath("ATP.cif")
        cif_file.write_text("data_ATP")
        mock_read.return_value = "data_ATP"

        paths = PathsConfig(prd=str(tmp_path))
        content, filename = resolve_cif("atp", paths, ccd_def=True)

        assert content == "data_ATP"
        assert filename == "atp.cif"

    @patch("view_cif.resolver.is_pdb_code", return_value=False)
    def test_resolve_chem_comp_missing_path(self, mock_is_pdb):
        with pytest.raises(SystemExit, match="chem_comp"):
            resolve_cif("atp", PathsConfig())
