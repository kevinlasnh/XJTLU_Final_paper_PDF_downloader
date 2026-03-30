"""
Legacy compatibility wrapper for URL parsing.
"""

import sys
from pathlib import Path
from typing import Tuple

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from xjtlu_downloader.core.url_parser import parse_viewer_url as parse_viewer_url_model
from xjtlu_downloader.core.url_parser import validate_url as validate_url_impl


def parse_viewer_url(viewer_url: str) -> dict:
    """Keep the old dict-based interface while delegating to the new core."""
    return parse_viewer_url_model(viewer_url).to_legacy_dict()


def validate_url(url: str) -> Tuple[bool, str]:
    """Keep the old tuple-based interface while delegating to the new core."""
    return validate_url_impl(url)


if __name__ == "__main__":
    test_url = (
        "https://etd.xjtlu.edu.cn/static/readonline/web/viewer.html?"
        "file=%2Fapi%2Fv1%2FFile%2FBrowserFile%3FdbCode%3DEXAMXJTLU"
        "%26recordId%3D15798%26dbId%3D3%26flag%3D0%26timestamp%3D1765788896"
        "%26signature%3D94adec6e1c4211f29b92eeb00b4c1b358127bbac3601581d378bbbdda885af13"
        "%26clientIp%3D180.208.58.213#page=1&zoom=auto"
    )

    result = parse_viewer_url(test_url)
    print("Parse Result:")
    print(f"  Success: {result['success']}")
    print(f"  Record ID: {result['record_id']}")
    print(f"  DB Code: {result['db_code']}")
    print(f"  Clean URL: {result['viewer_url'][:60]}...")
