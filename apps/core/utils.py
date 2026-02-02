"""
Core utility functions for BWIP.

Provides common utility functions used across the application.
"""

import re
from datetime import datetime
from typing import Any


def strip_html_tags(text: str) -> str:
    """
    Remove HTML tags from a string.

    Args:
        text: String potentially containing HTML tags.

    Returns:
        String with all HTML tags removed.

    Example:
        >>> strip_html_tags("<p>Hello <strong>World</strong></p>")
        'Hello World'
    """
    if not text:
        return ""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.

    Args:
        text: String to truncate.
        max_length: Maximum length including suffix.
        suffix: String to append if truncated.

    Returns:
        Truncated string with suffix if it exceeds max_length.

    Example:
        >>> truncate_string("Hello World", 8)
        'Hello...'
    """
    if not text or len(text) <= max_length:
        return text or ""
    return text[: max_length - len(suffix)] + suffix


def format_date_irish(date: datetime | None, include_time: bool = False) -> str:
    """
    Format a date in Irish date format (DD/MM/YYYY).

    Args:
        date: Datetime object to format.
        include_time: Whether to include time in the output.

    Returns:
        Formatted date string.

    Example:
        >>> from datetime import datetime
        >>> format_date_irish(datetime(2024, 1, 15, 14, 30))
        '15/01/2024'
        >>> format_date_irish(datetime(2024, 1, 15, 14, 30), include_time=True)
        '15/01/2024 14:30'
    """
    if not date:
        return ""
    if include_time:
        return date.strftime("%d/%m/%Y %H:%M")
    return date.strftime("%d/%m/%Y")


def safe_get(dictionary: dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a nested dictionary value using dot notation.

    Args:
        dictionary: Dictionary to search.
        key: Key using dot notation for nested access (e.g., "user.profile.name").
        default: Default value if key not found.

    Returns:
        Value at the key path or default.

    Example:
        >>> data = {"user": {"profile": {"name": "John"}}}
        >>> safe_get(data, "user.profile.name")
        'John'
        >>> safe_get(data, "user.profile.age", 0)
        0
    """
    keys = key.split(".")
    result = dictionary
    for k in keys:
        if isinstance(result, dict):
            result = result.get(k)
        else:
            return default
        if result is None:
            return default
    return result


def generate_filename(prefix: str, extension: str, include_timestamp: bool = True) -> str:
    """
    Generate a unique filename with optional timestamp.

    Args:
        prefix: Prefix for the filename.
        extension: File extension (without dot).
        include_timestamp: Whether to include timestamp in filename.

    Returns:
        Generated filename.

    Example:
        >>> generate_filename("poster", "pdf")
        'poster_20240115_143022.pdf'
    """
    if include_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
    return f"{prefix}.{extension}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: Original filename.

    Returns:
        Sanitized filename safe for filesystem.

    Example:
        >>> sanitize_filename("Beach Report 2024/01.pdf")
        'Beach_Report_2024_01.pdf'
    """
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    # Remove any character that isn't alphanumeric, underscore, hyphen, or period
    filename = re.sub(r"[^\w\-.]", "", filename)
    # Remove multiple consecutive underscores
    filename = re.sub(r"_+", "_", filename)
    return filename
