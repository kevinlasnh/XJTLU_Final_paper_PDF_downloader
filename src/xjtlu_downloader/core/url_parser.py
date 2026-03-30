"""Validation and parsing for XJTLU ETD viewer URLs."""

from typing import Tuple
from urllib.parse import parse_qs, unquote, urlparse

from xjtlu_downloader.domain.models import ParsedViewerUrl


def parse_viewer_url(viewer_url: str) -> ParsedViewerUrl:
    """Parse a viewer URL into structured metadata."""
    result = ParsedViewerUrl()

    try:
        clean_url = viewer_url.split("#")[0].strip()
        result.viewer_url = clean_url

        parsed = urlparse(clean_url)
        query_params = parse_qs(parsed.query)

        if "file" not in query_params:
            result.error = "链接不完整：缺少 'file' 参数（请确保复制的是完整的浏览器地址栏链接）"
            return result

        decoded_file_path = unquote(query_params["file"][0])
        file_parsed = urlparse(decoded_file_path)
        file_query = parse_qs(file_parsed.query)

        if "recordId" in file_query:
            result.record_id = file_query["recordId"][0]
        if "dbCode" in file_query:
            result.db_code = file_query["dbCode"][0]

        result.success = True
        return result
    except Exception as exc:
        result.error = f"链接解析出错：{exc}（链接格式可能有问题，请重新复制）"
        return result


def validate_url(url: str) -> Tuple[bool, str]:
    """Validate whether the input looks like an ETD viewer URL."""
    if not url or not url.strip():
        return False, "请输入URL链接（你还没有粘贴任何链接哦）"

    url = url.strip()

    if not url.startswith("http"):
        return False, "链接格式错误：必须以 http:// 或 https:// 开头（你可能复制错了）"

    if "etd.xjtlu.edu.cn" not in url:
        return False, "链接来源错误：必须是 etd.xjtlu.edu.cn 网站的链接（请从西浦ETD系统复制）"

    if "viewer.html" not in url and "file=" not in url:
        return False, "链接类型错误：这不是PDF查看器的链接（请在查看PDF时复制浏览器地址栏的完整链接）"

    return True, ""
