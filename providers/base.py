"""
providers/base.py
=================
Shared constants and helper functions used by all data providers.
"""

from datetime import datetime, timedelta

# Fixed historical dates to compare against current price
FIXED_DATES = {
    'april1_2025':    '2025-04-01',
    'october1_2025':  '2025-10-01',
    'december1_2025': '2025-12-01',
}


def find_closest_date(dates: list, target_date: str) -> str | None:
    """
    Find the nearest available trading day within ±7 calendar days of target_date.
    Searches outward from the target (day 0, +1, -1, +2, -2, ...).
    Returns None if no match found within 7 days.
    """
    target = datetime.strptime(target_date, '%Y-%m-%d')
    for delta in range(8):
        for direction in [1, -1]:
            candidate = target + timedelta(days=delta * direction)
            candidate_str = candidate.strftime('%Y-%m-%d')
            if candidate_str in dates:
                return candidate_str
    return None


def calculate_change(current: float, previous: float) -> tuple:
    """
    Calculate the absolute change and percentage change between two prices.
    Returns (change, percent_change) both rounded to 2 decimal places.
    """
    change = current - previous
    percent_change = (change / previous * 100) if previous != 0 else 0
    return round(change, 2), round(percent_change, 2)
