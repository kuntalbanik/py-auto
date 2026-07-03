"""Utility helper functions"""

import re
import hashlib
from urllib.parse import urlparse
from typing import Dict, Any, Optional


def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def get_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return ""


def get_path(url: str) -> str:
    """Extract path from URL"""
    try:
        parsed = urlparse(url)
        return parsed.path
    except Exception:
        return ""


def sanitize_filename(filename: str) -> str:
    """Sanitize string for use as filename"""
    sanitized = re.sub(r'[^\w\s-]', '', filename)
    sanitized = re.sub(r'[-\s]+', '-', sanitized)
    return sanitized.strip('-_')


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to maximum length"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def calculate_reading_time(text: str) -> int:
    """Estimate reading time in minutes"""
    if not text:
        return 0
    words = len(text.split())
    return max(1, round(words / 200))  # Average reading speed


def extract_emails(text: str) -> list:
    """Extract email addresses from text"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return list(set(re.findall(pattern, text)))


def extract_phone_numbers(text: str) -> list:
    """Extract phone numbers from text"""
    pattern = r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'
    return list(set(re.findall(pattern, text)))


def hash_content(content: str) -> str:
    """Generate MD5 hash of content"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def format_bytes(size: int) -> str:
    """Format byte size to human readable"""
    if size == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size_float = float(size)
    
    while size_float >= 1024.0 and i < len(size_names) - 1:
        size_float /= 1024.0
        i += 1
    
    return f"{size_float:.1f} {size_names[i]}"


def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result
