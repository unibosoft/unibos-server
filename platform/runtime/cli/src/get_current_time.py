#!/usr/bin/env python3
"""Get current Istanbul time for version updates"""

from datetime import datetime, timezone, timedelta

def get_istanbul_time():
    """Get current time in Istanbul timezone"""
    # Istanbul is UTC+3
    istanbul_tz = timezone(timedelta(hours=3))
    return datetime.now(istanbul_tz)

if __name__ == "__main__":
    now = get_istanbul_time()
    print(f"Current Istanbul time: {now.strftime('%Y-%m-%d %H:%M:%S %z')}")
    print(f"Build number format: {now.strftime('%Y%m%d_%H%M')}")
    print(f"For VERSION.json: {now.strftime('%Y-%m-%d %H:%M:%S +03:00')}")