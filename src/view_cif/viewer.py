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
        if f.is_file() and f.stat().st_mtime < cutoff:
            f.unlink()


def write_cache(content: str, filename: str, cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    output = cache_dir.joinpath(filename)
    output.write_text(content)
    return output


def open_in_editor(filepath: Path, editor: str) -> None:
    subprocess.Popen([editor, str(filepath)])
