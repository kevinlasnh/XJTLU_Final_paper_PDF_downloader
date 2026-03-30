"""File-system helpers shared by UI and downloader layers."""

from pathlib import Path


def ensure_unique_filepath(filepath: Path) -> Path:
    """Append a counter when the target file already exists."""
    if not filepath.exists():
        return filepath

    base = filepath.stem
    ext = filepath.suffix
    parent = filepath.parent
    counter = 1

    while True:
        candidate = parent / f"{base}_{counter}{ext}"
        if not candidate.exists():
            return candidate
        counter += 1


def format_file_size(size_bytes: int) -> str:
    """Format file size in a human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"
