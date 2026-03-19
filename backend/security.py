"""Security utilities for XSS sanitization and input cleaning"""
import re
import html


def sanitize_string(value: str) -> str:
    """Remove potential XSS payloads from a string"""
    if not isinstance(value, str):
        return value
    # Remove script tags and event handlers
    value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', value, flags=re.IGNORECASE)
    value = re.sub(r'javascript\s*:', '', value, flags=re.IGNORECASE)
    value = re.sub(r'data\s*:\s*text/html', '', value, flags=re.IGNORECASE)
    # Escape HTML entities for plain text fields
    value = html.escape(value, quote=True)
    return value.strip()


def sanitize_dict(data: dict, skip_keys: set = None) -> dict:
    """Recursively sanitize all string values in a dictionary"""
    skip_keys = skip_keys or set()
    cleaned = {}
    for key, value in data.items():
        if key in skip_keys:
            cleaned[key] = value
        elif isinstance(value, str):
            cleaned[key] = sanitize_string(value)
        elif isinstance(value, dict):
            cleaned[key] = sanitize_dict(value, skip_keys)
        else:
            cleaned[key] = value
    return cleaned
