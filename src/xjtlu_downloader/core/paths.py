"""Cross-platform application paths."""

import os
import sys
from pathlib import Path


APP_DIR_NAME = "XJTLU_PDF_Downloader"


def get_app_data_dir() -> Path:
    """Return the writable per-user application data directory."""
    if sys.platform == "win32":
        base_dir = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base_dir = Path.home() / "Library" / "Application Support"
    else:
        base_dir = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))

    app_dir = base_dir / APP_DIR_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_browser_profile_dir() -> Path:
    """Return the persistent browser profile directory used by the app."""
    profile_dir = get_app_data_dir() / "playwright-profile"
    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir
