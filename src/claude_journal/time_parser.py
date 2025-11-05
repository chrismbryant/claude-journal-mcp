"""Natural language time parsing for journal queries."""

from datetime import datetime, timedelta
from typing import Tuple
import re


def parse_time_expression(expression: str) -> Tuple[str, str]:
    """Parse natural language time expression to date range.

    Args:
        expression: Natural language time expression like:
                   - "last week", "last month", "last 3 days"
                   - "yesterday", "today"
                   - "january", "january 2024"
                   - "2024-01-15" (ISO date)

    Returns:
        Tuple of (start_date, end_date) in ISO format

    Examples:
        >>> parse_time_expression("last week")
        ('2024-01-01T00:00:00', '2024-01-08T23:59:59')
    """
    expression = expression.lower().strip()
    now = datetime.now()

    # Today
    if expression == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start.isoformat(), end.isoformat()

    # Yesterday
    if expression == "yesterday":
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start.isoformat(), end.isoformat()

    # This week
    if expression in ["this week", "current week"]:
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start.isoformat(), end.isoformat()

    # Last N days/weeks/months
    last_n_pattern = r"last (\d+) (day|days|week|weeks|month|months)"
    match = re.match(last_n_pattern, expression)
    if match:
        count = int(match.group(1))
        unit = match.group(2)

        if "day" in unit:
            start = now - timedelta(days=count)
        elif "week" in unit:
            start = now - timedelta(weeks=count)
        elif "month" in unit:
            # Approximate: 30 days per month
            start = now - timedelta(days=count * 30)

        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start.isoformat(), end.isoformat()

    # Last week/month/year
    if expression == "last week":
        end = now - timedelta(days=now.weekday() + 1)
        start = end - timedelta(days=6)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start.isoformat(), end.isoformat()

    if expression == "last month":
        # Go to first day of current month
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Go back one day to get last day of previous month
        end = first_of_month - timedelta(days=1)
        # Get first day of previous month
        start = end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start.isoformat(), end.isoformat()

    if expression == "last year":
        start = datetime(now.year - 1, 1, 1, 0, 0, 0)
        end = datetime(now.year - 1, 12, 31, 23, 59, 59, 999999)
        return start.isoformat(), end.isoformat()

    # This month/year
    if expression in ["this month", "current month"]:
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start.isoformat(), end.isoformat()

    if expression in ["this year", "current year"]:
        start = datetime(now.year, 1, 1, 0, 0, 0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start.isoformat(), end.isoformat()

    # Month names
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12
    }

    # Month with optional year (e.g., "january" or "january 2024")
    month_pattern = r"(january|february|march|april|may|june|july|august|september|october|november|december)(?:\s+(\d{4}))?"
    match = re.match(month_pattern, expression)
    if match:
        month_name = match.group(1)
        year = int(match.group(2)) if match.group(2) else now.year
        month = months[month_name]

        start = datetime(year, month, 1, 0, 0, 0)

        # Get last day of month
        if month == 12:
            end = datetime(year, 12, 31, 23, 59, 59, 999999)
        else:
            next_month = datetime(year, month + 1, 1)
            end = next_month - timedelta(days=1)
            end = end.replace(hour=23, minute=59, second=59, microsecond=999999)

        return start.isoformat(), end.isoformat()

    # ISO date format (YYYY-MM-DD)
    iso_date_pattern = r"(\d{4})-(\d{2})-(\d{2})"
    match = re.match(iso_date_pattern, expression)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        start = datetime(year, month, day, 0, 0, 0)
        end = datetime(year, month, day, 23, 59, 59, 999999)
        return start.isoformat(), end.isoformat()

    # If we can't parse, default to last 7 days
    start = now - timedelta(days=7)
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start.isoformat(), end.isoformat()
