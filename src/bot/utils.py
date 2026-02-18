import re
from datetime import datetime, timedelta


def parse_time(text: str) -> datetime | None:
    """Parse flexible time input into the closest past datetime.

    Supports: 14:30, 2 PM, 2:00AM, 02:00 AM, 11:23PM, 23:23, 11:23, 23
    If no AM/PM is given the result is rolled back to yesterday when needed.
    """
    m = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$", text.strip().lower())
    if not m:
        return None

    hour = int(m.group(1))
    minute = int(m.group(2)) if m.group(2) else 0
    period = m.group(3)

    if period:
        if hour < 1 or hour > 12:
            return None
        if period == "am":
            hour = 0 if hour == 12 else hour
        else:
            hour = hour if hour == 12 else hour + 12
    else:
        if hour > 23:
            return None

    if minute > 59:
        return None

    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if target > now:
        target -= timedelta(days=1)

    return target
