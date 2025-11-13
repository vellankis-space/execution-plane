"""
Timezone utilities for IST (Indian Standard Time) support
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import pytz

# IST timezone - UTC+5:30
IST = pytz.timezone('Asia/Kolkata')


def now_ist() -> datetime:
    """
    Get current datetime in IST timezone
    
    Returns:
        datetime: Current datetime with IST timezone
    """
    return datetime.now(IST)


def utc_to_ist(utc_dt: datetime) -> datetime:
    """
    Convert UTC datetime to IST
    
    Args:
        utc_dt: UTC datetime (can be naive or aware)
    
    Returns:
        datetime: Datetime in IST timezone
    """
    if utc_dt is None:
        return None
    
    # If naive, assume it's UTC
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)
    
    # Convert to IST
    return utc_dt.astimezone(IST)


def to_ist_isoformat(dt: Optional[datetime]) -> Optional[str]:
    """
    Convert datetime to IST ISO format string
    
    Args:
        dt: Datetime object (can be naive or aware)
    
    Returns:
        str: ISO format string in IST, or None if dt is None
    """
    if dt is None:
        return None
    
    # Convert to IST first
    ist_dt = utc_to_ist(dt) if dt.tzinfo is not None or isinstance(dt, datetime) else dt
    
    # If still naive, localize to IST
    if ist_dt.tzinfo is None:
        ist_dt = IST.localize(ist_dt)
    
    return ist_dt.isoformat()


def parse_ist_datetime(date_string: str) -> datetime:
    """
    Parse ISO format string to IST datetime
    
    Args:
        date_string: ISO format datetime string
    
    Returns:
        datetime: Datetime in IST timezone
    """
    dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    return utc_to_ist(dt)


def format_ist_datetime(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S IST") -> Optional[str]:
    """
    Format datetime in IST with custom format
    
    Args:
        dt: Datetime object
        format_str: Format string (default includes IST suffix)
    
    Returns:
        str: Formatted datetime string, or None if dt is None
    """
    if dt is None:
        return None
    
    ist_dt = utc_to_ist(dt)
    return ist_dt.strftime(format_str)


def get_ist_offset() -> str:
    """
    Get IST timezone offset as string
    
    Returns:
        str: Timezone offset (e.g., "+05:30")
    """
    return "+05:30"
