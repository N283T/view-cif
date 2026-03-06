"""Cache management and editor launching."""

import subprocess
import time
from pathlib import Path


CACHE_MAX_AGE_DAYS = 7


def cleanup_old_cache(cache_dir: Path) -> None:
    if not cache_dir.exists():
        return

    cutoff = time.time() - (CACHE_MAX_AGE_DAYS * 86400)
    for f in cache_dir.iterdir():
        try:
            if f.is_file() and f.stat().st_mtime < cutoff:
                f.unlink()
        except OSError:
            pass


def write_cache(content: str, filename: str, cache_dir: Path) -> Path:
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        output = cache_dir.joinpath(filename)
        output.write_text(content)
    except PermissionError:
        raise SystemExit(
            f"Error: Cannot write to cache directory {cache_dir}. "
            "Check permissions or set a different cache_dir in config."
        )
    except OSError as e:
        raise SystemExit(f"Error: Failed to write cache file: {e}")
    return output


def open_in_editor(filepath: Path, editor: str) -> None:
    try:
        subprocess.Popen([editor, str(filepath)])
    except FileNotFoundError:
        raise SystemExit(
            f"Error: Editor '{editor}' not found. "
            f"Install it or set a different editor in "
            f"~/.config/view-cif/config.yaml (editor: <command>)"
        )
    except OSError as e:
        raise SystemExit(f"Error: Failed to launch editor '{editor}': {e}")
