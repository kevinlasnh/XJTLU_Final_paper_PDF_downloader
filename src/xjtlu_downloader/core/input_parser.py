"""Helpers for extracting viewer URLs from free-form user input."""

import re


URL_PATTERN = re.compile(r"https?://[^\s\"'<>]+")


def extract_urls_from_text(text: str) -> list[str]:
    """Extract candidate URLs from arbitrary pasted text."""
    candidates = []

    for match in URL_PATTERN.findall(text or ""):
        normalized = match.strip().rstrip("),.;]")
        if normalized:
            candidates.append(normalized)

    return candidates
