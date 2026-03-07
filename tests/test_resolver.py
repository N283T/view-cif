"""Tests for resolver module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from view_cif.config import PathsConfig
from view_cif.resolver import (
    _bird_subdir,
    _find_cif_file,
    _require_path,
    resolve_cif,
)


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

    def test_finds_nested_cif(self, tmp_path: Path):
        nested = tmp_path.joinpath("P", "ABC")
        nested.mkdir(parents=True)
        cif_file = nested.joinpath("ABC.cif")
        cif_file.write_text("data_ABC")
        result = _find_cif_file("ABC", str(tmp_path))
        assert result == cif_file

    def test_finds_nested_flat_cif(self, tmp_path: Path):
        nested = tmp_path.joinpath("9")
        nested.mkdir()
        cif_file = nested.joinpath("ABC.cif")
        cif_file.write_text("data_ABC")
        result = _find_cif_file("ABC", str(tmp_path))
        assert result == cif_file

    def test_raises_on_missing(self, tmp_path: Path):
        with pytest.raises(SystemExit, match="ABC.cif not found"):
            _find_cif_file("ABC", str(tmp_path))


class TestBirdSubdir:
    def test_prd_prefix(self):
        assert _bird_subdir("PRD_000010") == "prd"

    def test_prdcc_prefix(self):
        assert _bird_subdir("PRDCC_000240") == "prdcc"

    def test_fam_prefix(self):
        assert _bird_subdir("FAM_000160") == "family"

    def test_case_insensitive(self):
        assert _bird_subdir("prd_000010") == "prd"
        assert _bird_subdir("prdcc_000240") == "prdcc"
        assert _bird_subdir("fam_000160") == "family"

    def test_no_match(self):
        assert _bird_subdir("ATP") is None
        assert _bird_subdir("1abc") is None

    def test_prdcc_not_matched_as_prd(self):
        # PRDCC_ must match prdcc, not prd
        assert _bird_subdir("PRDCC_000001") == "prdcc"


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
                    "entries",
                    "divided",
                    "ab",
                    "pdb_00001abc",
                    "pdb_00001abc_xyz-enrich.cif.gz",
                )
            )
        )

    @patch("view_cif.resolver.is_pdb_code", return_value=True)
    def test_resolve_pdb_code_next_gen_missing_path(self, mock_is_pdb):
        paths = PathsConfig()
        with pytest.raises(SystemExit, match="pdb_next_gen"):
            resolve_cif("1abc", paths, next_gen=True)

    # BIRD individual lookup tests
    @patch("view_cif.resolver._safe_read_cif")
    @patch("view_cif.resolver.is_pdb_code", return_value=False)
    def test_resolve_prd_individual(self, mock_is_pdb, mock_read, tmp_path: Path):
        prd_dir = tmp_path.joinpath("prd", "0")
        prd_dir.mkdir(parents=True)
        cif_file = prd_dir.joinpath("PRD_000010.cif")
        cif_file.write_text("data_PRD")
        mock_read.return_value = "data_PRD"

        paths = PathsConfig(prd=str(tmp_path))
        content, filename = resolve_cif("PRD_000010", paths)

        assert content == "data_PRD"
        assert filename == "PRD_000010.cif"

    @patch("view_cif.resolver._safe_read_cif")
    @patch("view_cif.resolver.is_pdb_code", return_value=False)
    def test_resolve_prdcc_individual(self, mock_is_pdb, mock_read, tmp_path: Path):
        prdcc_dir = tmp_path.joinpath("prdcc", "0")
        prdcc_dir.mkdir(parents=True)
        cif_file = prdcc_dir.joinpath("PRDCC_000240.cif")
        cif_file.write_text("data_PRDCC")
        mock_read.return_value = "data_PRDCC"

        paths = PathsConfig(prd=str(tmp_path))
        content, filename = resolve_cif("PRDCC_000240", paths)

        assert content == "data_PRDCC"
        assert filename == "PRDCC_000240.cif"

    @patch("view_cif.resolver._safe_read_cif")
    @patch("view_cif.resolver.is_pdb_code", return_value=False)
    def test_resolve_fam_individual(self, mock_is_pdb, mock_read, tmp_path: Path):
        fam_dir = tmp_path.joinpath("family", "0")
        fam_dir.mkdir(parents=True)
        cif_file = fam_dir.joinpath("FAM_000160.cif")
        cif_file.write_text("data_FAM")
        mock_read.return_value = "data_FAM"

        paths = PathsConfig(prd=str(tmp_path))
        content, filename = resolve_cif("FAM_000160", paths)

        assert content == "data_FAM"
        assert filename == "FAM_000160.cif"

    @patch("view_cif.resolver._safe_read_cif")
    @patch("view_cif.resolver.is_pdb_code", return_value=False)
    def test_resolve_bird_case_insensitive(self, mock_is_pdb, mock_read, tmp_path: Path):
        prd_dir = tmp_path.joinpath("prd", "0")
        prd_dir.mkdir(parents=True)
        cif_file = prd_dir.joinpath("PRD_000010.cif")
        cif_file.write_text("data_PRD")
        mock_read.return_value = "data_PRD"

        paths = PathsConfig(prd=str(tmp_path))
        content, filename = resolve_cif("prd_000010", paths)

        assert content == "data_PRD"
        assert filename == "PRD_000010.cif"

    @patch("view_cif.resolver.is_pdb_code", return_value=False)
    def test_resolve_bird_missing_path(self, mock_is_pdb):
        paths = PathsConfig()
        with pytest.raises(SystemExit, match="prd"):
            resolve_cif("PRD_000010", paths)

    # Bulk file tests
    @patch("view_cif.resolver._safe_read_cif")
    @patch("view_cif.resolver.is_pdb_code", return_value=False)
    def test_resolve_prd_bulk(self, mock_is_pdb, mock_read):
        mock_read.return_value = "prd_data"

        paths = PathsConfig(bird="/data/bird")
        content, filename = resolve_cif("prd", paths)

        assert content == "prd_data"
        assert filename == "prd.cif"
        mock_read.assert_called_once_with(
            str(Path("/data/bird").joinpath("prd-all.cif.gz"))
        )

    @patch("view_cif.resolver._safe_read_cif")
    @patch("view_cif.resolver.is_pdb_code", return_value=False)
    def test_resolve_prdcc_bulk(self, mock_is_pdb, mock_read):
        mock_read.return_value = "prdcc_data"

        paths = PathsConfig(bird="/data/bird")
        content, filename = resolve_cif("prdcc", paths)

        assert content == "prdcc_data"
        assert filename == "prdcc.cif"
        mock_read.assert_called_once_with(
            str(Path("/data/bird").joinpath("prdcc-all.cif.gz"))
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
    def test_resolve_prd_bulk_missing_path(self, mock_is_pdb):
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

    @patch("view_cif.resolver.is_pdb_code", return_value=False)
    def test_resolve_chem_comp_missing_path(self, mock_is_pdb):
        with pytest.raises(SystemExit, match="chem_comp"):
            resolve_cif("atp", PathsConfig())
