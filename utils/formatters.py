"""
Data formatting utilities for ReqCockpit
"""
from datetime import datetime, timedelta
from typing import Optional
from config import NormalizedStatus


def format_status(status: str) -> str:
    """
    Format status value for display
    
    Args:
        status: Status value to format
        
    Returns:
        Formatted status string
    """
    from .constants import STATUS_LABELS
    
    if not status:
        return STATUS_LABELS.get(NormalizedStatus.NOT_SET.value, "Not Set")
    
    return STATUS_LABELS.get(status, status)


def format_date(date_obj: Optional[datetime]) -> str:
    """
    Format datetime to date string (YYYY-MM-DD)
    
    Args:
        date_obj: Datetime object to format
        
    Returns:
        Formatted date string
    """
    if not date_obj:
        return ""
    
    if isinstance(date_obj, str):
        return date_obj
    
    return date_obj.strftime("%Y-%m-%d")


def format_datetime(date_obj: Optional[datetime]) -> str:
    """
    Format datetime to full datetime string (YYYY-MM-DD HH:MM:SS)
    
    Args:
        date_obj: Datetime object to format
        
    Returns:
        Formatted datetime string
    """
    if not date_obj:
        return ""
    
    if isinstance(date_obj, str):
        return date_obj
    
    return date_obj.strftime("%Y-%m-%d %H:%M:%S")


def format_duration(start: Optional[datetime], end: Optional[datetime]) -> str:
    """
    Format duration between two datetimes
    
    Args:
        start: Start datetime
        end: End datetime
        
    Returns:
        Formatted duration string (e.g., "2 days, 3 hours")
    """
    if not start or not end:
        return ""
    
    if end < start:
        return ""
    
    duration = end - start
    
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    
    return ", ".join(parts) if parts else "0 minutes"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format number as percentage
    
    Args:
        value: Value to format (0-100)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimals}f}%"


def format_count(count: int) -> str:
    """
    Format count with thousands separator
    
    Args:
        count: Number to format
        
    Returns:
        Formatted count string
    """
    return f"{count:,}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    
    return f"{size_bytes:.1f} TB"


def format_status_badge(status: str) -> str:
    """
    Format status for badge display
    
    Args:
        status: Status value
        
    Returns:
        Formatted badge string
    """
    from .constants import STATUS_ICONS
    
    icon = STATUS_ICONS.get(status, "")
    label = format_status(status)
    
    return f"{icon} {label}" if icon else label
