"""Typed enums shared by the downloader layers."""

from enum import Enum


class DownloadErrorCode(str, Enum):
    """Stable error codes for downloader results."""

    NONE = "none"
    INTERNAL_ERROR = "internal_error"
    NETWORK_ERROR = "network_error"
    VIEWER_ERROR = "viewer_error"
    TIMEOUT = "timeout"
    INVALID_PDF = "invalid_pdf"
    SAVE_ERROR = "save_error"
    NO_DATA = "no_data"
    BROWSER_MISSING = "browser_missing"
    ACCESS_DENIED = "access_denied"
    PROFILE_IN_USE = "profile_in_use"
