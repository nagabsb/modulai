"""
Input sanitization utilities for XSS prevention.
"""
import bleach
import re


def sanitize_text(text: str) -> str:
    """Strip all HTML tags from text input"""
    if not text:
        return text
    return bleach.clean(text, tags=[], attributes={}, strip=True).strip()


def sanitize_email(email: str) -> str:
    """Validate and sanitize email"""
    if not email:
        return email
    cleaned = sanitize_text(email).lower().strip()
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', cleaned):
        raise ValueError("Format email tidak valid")
    return cleaned


def sanitize_html_content(html: str) -> str:
    """Sanitize HTML content - allow safe tags only"""
    if not html:
        return html
    allowed_tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'p', 'br', 'hr', 'div', 'span',
        'strong', 'b', 'em', 'i', 'u',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'ul', 'ol', 'li',
        'a', 'img',
        'pre', 'code',
        'sub', 'sup',
    ]
    allowed_attrs = {
        '*': ['style', 'class', 'id'],
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'width', 'height'],
        'td': ['colspan', 'rowspan'],
        'th': ['colspan', 'rowspan'],
    }
    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=False)
