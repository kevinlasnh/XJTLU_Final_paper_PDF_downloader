"""Runtime environment helpers for packaged builds."""

import os
import sys
from pathlib import Path


def configure_runtime_environment() -> None:
    """Configure runtime paths when running from a packaged desktop build."""
    if not getattr(sys, "frozen", False):
        return

    base_dir = Path(sys.executable).resolve().parent
    candidate_roots = []

    if getattr(sys, "_MEIPASS", None):
        candidate_roots.append(Path(sys._MEIPASS))

    candidate_roots.extend(
        [
            base_dir / "_internal",
            base_dir,
        ]
    )

    for root in candidate_roots:
        browser_dir = root / "ms-playwright"
        if browser_dir.exists():
            os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(browser_dir))
            return
