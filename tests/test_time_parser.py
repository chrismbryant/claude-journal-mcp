"""Tests for natural language time parsing."""

import pytest
from datetime import datetime, timedelta
from claude_journal.time_parser import parse_time_expression


class TestBasicExpressions:
    """Test basic time expressions."""

    def test_today(self):
        """Test 'today' expression."""
        start, end = parse_time_expression("today")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        assert start_dt.hour == 0
        assert start_dt.minute == 0
        assert end_dt.hour == 23
        assert end_dt.minute == 59

        # Both should be today
        today = datetime.now().date()
        assert start_dt.date() == today
        assert end_dt.date() == today

    def test_yesterday(self):
        """Test 'yesterday' expression."""
        start, end = parse_time_expression("yesterday")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        yesterday = (datetime.now() - timedelta(days=1)).date()
        assert start_dt.date() == yesterday
        assert end_dt.date() == yesterday

        assert start_dt.hour == 0
        assert end_dt.hour == 23

    def test_case_insensitive(self):
        """Test that expressions are case insensitive."""
        result1 = parse_time_expression("TODAY")
        result2 = parse_time_expression("today")
        result3 = parse_time_expression("ToDay")

        assert result1 == result2 == result3


class TestWeekExpressions:
    """Test week-based expressions."""

    def test_this_week(self):
        """Test 'this week' expression."""
        start, end = parse_time_expression("this week")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        # Start should be Monday of this week
        now = datetime.now()
        expected_monday = (now - timedelta(days=now.weekday())).date()
        assert start_dt.date() == expected_monday

        # End should be today
        assert end_dt.date() == now.date()

    def test_current_week(self):
        """Test 'current week' as alias."""
        result1 = parse_time_expression("this week")
        result2 = parse_time_expression("current week")
        assert result1 == result2

    def test_last_week(self):
        """Test 'last week' expression."""
        start, end = parse_time_expression("last week")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        # Should be a 7-day range
        duration = end_dt - start_dt
        assert duration.days == 6  # 6 days difference (inclusive)

        # End should be before this week
        now = datetime.now()
        this_monday = now - timedelta(days=now.weekday())
        assert end_dt.date() < this_monday.date()


class TestMonthExpressions:
    """Test month-based expressions."""

    def test_this_month(self):
        """Test 'this month' expression."""
        start, end = parse_time_expression("this month")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        now = datetime.now()

        # Start should be first of this month
        assert start_dt.day == 1
        assert start_dt.month == now.month
        assert start_dt.year == now.year

        # End should be today
        assert end_dt.date() == now.date()

    def test_current_month(self):
        """Test 'current month' as alias."""
        result1 = parse_time_expression("this month")
        result2 = parse_time_expression("current month")
        assert result1 == result2

    def test_last_month(self):
        """Test 'last month' expression."""
        start, end = parse_time_expression("last month")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        # Should be first and last day of previous month
        assert start_dt.day == 1

        now = datetime.now()
        if now.month == 1:
            expected_month = 12
            expected_year = now.year - 1
        else:
            expected_month = now.month - 1
            expected_year = now.year

        assert start_dt.month == expected_month
        assert start_dt.year == expected_year
        assert end_dt.month == expected_month
        assert end_dt.year == expected_year


class TestYearExpressions:
    """Test year-based expressions."""

    def test_this_year(self):
        """Test 'this year' expression."""
        start, end = parse_time_expression("this year")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        now = datetime.now()

        # Start should be January 1st
        assert start_dt.month == 1
        assert start_dt.day == 1
        assert start_dt.year == now.year

        # End should be today
        assert end_dt.date() == now.date()

    def test_current_year(self):
        """Test 'current year' as alias."""
        result1 = parse_time_expression("this year")
        result2 = parse_time_expression("current year")
        assert result1 == result2

    def test_last_year(self):
        """Test 'last year' expression."""
        start, end = parse_time_expression("last year")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        now = datetime.now()
        last_year = now.year - 1

        # Should be January 1 to December 31 of last year
        assert start_dt.year == last_year
        assert start_dt.month == 1
        assert start_dt.day == 1

        assert end_dt.year == last_year
        assert end_dt.month == 12
        assert end_dt.day == 31


class TestRelativeExpressions:
    """Test relative 'last N' expressions."""

    def test_last_3_days(self):
        """Test 'last 3 days' expression."""
        start, end = parse_time_expression("last 3 days")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        # Should span approximately 3 days
        now = datetime.now()
        expected_start = (now - timedelta(days=3)).date()
        assert start_dt.date() == expected_start
        assert end_dt.date() == now.date()

    def test_last_day_singular(self):
        """Test 'last 1 day' (singular form)."""
        start, end = parse_time_expression("last 1 day")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        now = datetime.now()
        expected_start = (now - timedelta(days=1)).date()
        assert start_dt.date() == expected_start

    def test_last_2_weeks(self):
        """Test 'last 2 weeks' expression."""
        start, end = parse_time_expression("last 2 weeks")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        # Should span approximately 14 days
        duration = end_dt - start_dt
        assert duration.days >= 13  # At least 13 days

    def test_last_6_months(self):
        """Test 'last 6 months' expression."""
        start, end = parse_time_expression("last 6 months")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        # Should span approximately 180 days (6 * 30)
        duration = end_dt - start_dt
        assert duration.days >= 179  # At least 179 days (6*30-1)


class TestMonthNames:
    """Test month name expressions."""

    def test_january(self):
        """Test 'january' expression."""
        start, end = parse_time_expression("january")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        # Should be January 1-31 of current year
        now = datetime.now()
        assert start_dt.month == 1
        assert start_dt.day == 1
        assert start_dt.year == now.year

        assert end_dt.month == 1
        assert end_dt.day == 31
        assert end_dt.year == now.year

    def test_february(self):
        """Test 'february' expression."""
        start, end = parse_time_expression("february")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        assert start_dt.month == 2
        assert start_dt.day == 1

        assert end_dt.month == 2
        # February can be 28 or 29 days
        assert end_dt.day in [28, 29]

    def test_december(self):
        """Test 'december' expression."""
        start, end = parse_time_expression("december")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        assert start_dt.month == 12
        assert start_dt.day == 1

        assert end_dt.month == 12
        assert end_dt.day == 31

    def test_month_with_year(self):
        """Test 'january 2024' expression."""
        start, end = parse_time_expression("january 2024")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        assert start_dt.year == 2024
        assert start_dt.month == 1
        assert start_dt.day == 1

        assert end_dt.year == 2024
        assert end_dt.month == 1
        assert end_dt.day == 31

    def test_all_months(self):
        """Test all month names are recognized."""
        months = [
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december"
        ]

        for i, month in enumerate(months, 1):
            start, end = parse_time_expression(month)
            start_dt = datetime.fromisoformat(start)
            assert start_dt.month == i


class TestISODate:
    """Test ISO date format."""

    def test_iso_date_format(self):
        """Test '2024-01-15' format."""
        start, end = parse_time_expression("2024-01-15")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        assert start_dt.year == 2024
        assert start_dt.month == 1
        assert start_dt.day == 15

        # Should span single day
        assert start_dt.date() == end_dt.date()

        assert start_dt.hour == 0
        assert end_dt.hour == 23

    def test_iso_date_different_dates(self):
        """Test various ISO dates."""
        dates = [
            ("2023-12-25", 2023, 12, 25),
            ("2024-06-01", 2024, 6, 1),
            ("2025-03-30", 2025, 3, 30),
        ]

        for date_str, year, month, day in dates:
            start, end = parse_time_expression(date_str)
            start_dt = datetime.fromisoformat(start)

            assert start_dt.year == year
            assert start_dt.month == month
            assert start_dt.day == day


class TestFallback:
    """Test fallback behavior for unrecognized expressions."""

    def test_unknown_expression(self):
        """Test that unknown expressions default to last 7 days."""
        start, end = parse_time_expression("some random text xyz")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        # Should default to last 7 days
        now = datetime.now()
        expected_start = (now - timedelta(days=7)).date()

        assert start_dt.date() == expected_start
        assert end_dt.date() == now.date()

    def test_empty_string(self):
        """Test empty string defaults to last 7 days."""
        start, end = parse_time_expression("")

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        # Should span approximately 7 days
        duration = end_dt - start_dt
        assert duration.days >= 6


class TestTimeRanges:
    """Test that time ranges are correctly set."""

    def test_start_is_beginning_of_day(self):
        """Test that start times are set to beginning of day."""
        expressions = ["today", "yesterday", "last week", "january"]

        for expr in expressions:
            start, end = parse_time_expression(expr)
            start_dt = datetime.fromisoformat(start)

            assert start_dt.hour == 0
            assert start_dt.minute == 0
            assert start_dt.second == 0

    def test_end_is_end_of_day(self):
        """Test that end times are set to end of day."""
        expressions = ["today", "yesterday", "last week", "january"]

        for expr in expressions:
            start, end = parse_time_expression(expr)
            end_dt = datetime.fromisoformat(end)

            assert end_dt.hour == 23
            assert end_dt.minute == 59
            assert end_dt.second == 59

    def test_start_before_end(self):
        """Test that start is always before end."""
        expressions = [
            "today", "yesterday", "last week", "last month",
            "last year", "january", "last 3 days", "2024-01-15"
        ]

        for expr in expressions:
            start, end = parse_time_expression(expr)
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)

            assert start_dt <= end_dt, f"Failed for expression: {expr}"
