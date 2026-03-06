"""Tests for viewer module."""

import os
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from view_cif.viewer import cleanup_old_cache, open_in_editor, write_cache


class TestCleanupOldCache:
    def test_removes_old_files(self, tmp_path: Path):
        old_file = tmp_path.joinpath("old.cif")
        old_file.write_text("old content")
        old_mtime = time.time() - (10 * 86400)
        os.utime(old_file, (old_mtime, old_mtime))

        new_file = tmp_path.joinpath("new.cif")
        new_file.write_text("new content")

        cleanup_old_cache(tmp_path)

        assert not old_file.exists()
        assert new_file.exists()

    def test_noop_on_nonexistent_dir(self, tmp_path: Path):
        nonexistent = tmp_path.joinpath("does-not-exist")
        cleanup_old_cache(nonexistent)

    def test_skips_unremovable_files(self, tmp_path: Path):
        old_file = tmp_path.joinpath("old.cif")
        old_file.write_text("old content")
        old_mtime = time.time() - (10 * 86400)
        os.utime(old_file, (old_mtime, old_mtime))

        with patch.object(Path, "unlink", side_effect=PermissionError):
            cleanup_old_cache(tmp_path)

        assert old_file.exists()


class TestWriteCache:
    def test_writes_file(self, tmp_path: Path):
        output = write_cache("data_test\n_cell.length_a 10.0\n", "test.cif", tmp_path)
        assert output.exists()
        assert output.read_text() == "data_test\n_cell.length_a 10.0\n"

    def test_creates_cache_dir(self, tmp_path: Path):
        cache_dir = tmp_path.joinpath("sub", "dir")
        write_cache("content", "test.cif", cache_dir)
        assert cache_dir.joinpath("test.cif").exists()

    def test_raises_on_permission_error(self, tmp_path: Path):
        with patch.object(Path, "mkdir", side_effect=PermissionError):
            with pytest.raises(SystemExit, match="Cannot write to cache"):
                write_cache("content", "test.cif", tmp_path)


class TestOpenInEditor:
    @patch("view_cif.viewer.subprocess.Popen")
    def test_calls_editor(self, mock_popen, tmp_path: Path):
        filepath = tmp_path.joinpath("test.cif")
        filepath.write_text("content")
        open_in_editor(filepath, "vim")
        mock_popen.assert_called_once_with(["vim", str(filepath)])

    @patch("view_cif.viewer.subprocess.Popen", side_effect=FileNotFoundError)
    def test_raises_on_editor_not_found(self, mock_popen, tmp_path: Path):
        filepath = tmp_path.joinpath("test.cif")
        filepath.write_text("content")
        with pytest.raises(SystemExit, match="Editor 'nonexistent' not found"):
            open_in_editor(filepath, "nonexistent")

    @patch("view_cif.viewer.subprocess.Popen", side_effect=OSError("launch failed"))
    def test_raises_on_os_error(self, mock_popen, tmp_path: Path):
        filepath = tmp_path.joinpath("test.cif")
        filepath.write_text("content")
        with pytest.raises(SystemExit, match="Failed to launch editor"):
            open_in_editor(filepath, "vim")
