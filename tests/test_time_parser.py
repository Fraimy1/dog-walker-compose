"""Tests for the time parser utility."""
from datetime import datetime as real_datetime
from unittest.mock import patch

import pytest

from src.bot.utils import parse_time

FIXED_NOW = real_datetime(2024, 6, 15, 10, 0, 0)  # Saturday 10:00 AM


def _parse(text: str):
    """Parse with a fixed 'now' for deterministic results."""
    with patch("src.bot.utils.datetime") as mock_dt:
        mock_dt.now.return_value = FIXED_NOW
        mock_dt.side_effect = lambda *a, **kw: real_datetime(*a, **kw)
        return parse_time(text)


# ---------------------------------------------------------------------------
# Invalid inputs
# ---------------------------------------------------------------------------

def test_empty_string():
    assert parse_time("") is None


def test_letters_only():
    assert parse_time("abc") is None


def test_out_of_range_hour_24h():
    assert parse_time("25:00") is None


def test_out_of_range_minute():
    assert parse_time("10:60") is None


def test_out_of_range_12h_zero():
    assert parse_time("0 AM") is None


def test_out_of_range_12h_thirteen():
    assert parse_time("13 PM") is None


def test_random_text():
    assert parse_time("half past two") is None


def test_negative_hour():
    assert parse_time("-1:00") is None


# ---------------------------------------------------------------------------
# 24-hour format — past times (today)
# ---------------------------------------------------------------------------

def test_24h_simple_past():
    result = _parse("9:00")
    assert result is not None
    assert result.hour == 9
    assert result.minute == 0
    assert result.date() == FIXED_NOW.date()


def test_24h_with_minutes_past():
    result = _parse("9:30")
    assert result is not None
    assert result.hour == 9
    assert result.minute == 30


def test_24h_exact_now_stays_today():
    # 10:00 == now exactly — "target > now" is False, so stays today (not rolled back)
    result = _parse("10:00")
    assert result is not None
    assert result.date() == FIXED_NOW.date()
    assert result.hour == 10


def test_24h_future_rolls_back():
    result = _parse("23:00")
    assert result is not None
    assert result.date().day == FIXED_NOW.date().day - 1


def test_24h_no_minutes():
    result = _parse("9")
    assert result is not None
    assert result.hour == 9
    assert result.minute == 0


def test_24h_midnight():
    result = _parse("0:00")
    assert result is not None
    assert result.hour == 0
    assert result.minute == 0


def test_24h_max_valid():
    result = _parse("23:59")
    assert result is not None
    assert result.hour == 23
    assert result.minute == 59


# ---------------------------------------------------------------------------
# 12-hour format
# ---------------------------------------------------------------------------

def test_12h_am_past():
    result = _parse("9 AM")
    assert result is not None
    assert result.hour == 9


def test_12h_pm_future_rolls_back():
    # 2 PM = 14:00, which is in the future relative to FIXED_NOW (10:00)
    result = _parse("2 PM")
    assert result is not None
    assert result.hour == 14
    assert result.date().day == FIXED_NOW.date().day - 1


def test_12h_noon_rolls_back():
    # 12 PM = 12:00, future → rolls back
    result = _parse("12 PM")
    assert result is not None
    assert result.hour == 12
    assert result.date().day == FIXED_NOW.date().day - 1


def test_12h_midnight_am():
    # 12 AM = 0:00 (midnight)
    result = _parse("12 AM")
    assert result is not None
    assert result.hour == 0


def test_12h_with_minutes():
    result = _parse("9:30 AM")
    assert result is not None
    assert result.hour == 9
    assert result.minute == 30


def test_12h_no_space():
    result = _parse("9PM")
    assert result is not None
    assert result.hour == 21


def test_12h_lowercase():
    result = _parse("9am")
    assert result is not None
    assert result.hour == 9


def test_12h_uppercase():
    result = _parse("9AM")
    assert result is not None
    assert result.hour == 9


# ---------------------------------------------------------------------------
# Whitespace handling
# ---------------------------------------------------------------------------

def test_leading_trailing_whitespace():
    result = _parse("  9:00  ")
    assert result is not None
    assert result.hour == 9


def test_space_between_hour_and_am():
    result = _parse("9 am")
    assert result is not None
    assert result.hour == 9


# ---------------------------------------------------------------------------
# Return type and structure
# ---------------------------------------------------------------------------

def test_returns_datetime():
    result = _parse("8:00")
    assert isinstance(result, real_datetime)


def test_seconds_zeroed():
    result = _parse("8:45")
    assert result is not None
    assert result.second == 0
    assert result.microsecond == 0
