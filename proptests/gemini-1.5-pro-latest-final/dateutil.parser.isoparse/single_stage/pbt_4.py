from hypothesis import given, strategies as st
from dateutil.parser import isoparse
import datetime

# Summary: This strategy generates a wide variety of ISO 8601 datetime strings, including edge cases, to test the isoparse function.
@given(st.data())
def test_dateutil_parser_isoparse(data):
    # Generate year, month, day, hour, minute, second, and microsecond components.
    year = data.draw(st.integers(min_value=1, max_value=9999))
    month = data.draw(st.integers(min_value=1, max_value=12))
    day = data.draw(st.integers(min_value=1, max_value=28))  # Limit day to 28 to accommodate February
    hour = data.draw(st.integers(min_value=0, max_value=23))
    minute = data.draw(st.integers(min_value=0, max_value=59))
    second = data.draw(st.integers(min_value=0, max_value=59))
    microsecond = data.draw(st.integers(min_value=0, max_value=999999))

    # Generate optional components: time zone offset and separators.
    include_timezone = data.draw(st.booleans())
    separator = data.draw(st.sampled_from(["T", " "]))  # Test both T and space separators
    if include_timezone:
        timezone_hour_offset = data.draw(st.integers(min_value=-12, max_value=14))
        timezone_minute_offset = data.draw(st.integers(min_value=0, max_value=59))
        timezone_str = f"{timezone_hour_offset:+03d}:{timezone_minute_offset:02d}"
    else:
        timezone_str = "Z"

    # Construct the ISO 8601 datetime string with variations.
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    time_str = f"{hour:02d}:{minute:02d}:{second:02d}.{microsecond:06d}"
    dt_str = f"{date_str}{separator}{time_str}{timezone_str}"

    # Edge cases: Test midnight representation and incomplete date formats.
    if hour == 0 and minute == 0 and second == 0:
        dt_str_midnight = f"{date_str}{separator}24:00:00.000000{timezone_str}"
        parsed_midnight = isoparse(dt_str_midnight)
        assert parsed_midnight.hour == 0
        assert parsed_midnight.minute == 0
        assert parsed_midnight.second == 0

    incomplete_date_str = f"{year:04d}-{month:02d}"
    parsed_incomplete_date = isoparse(incomplete_date_str)
    assert parsed_incomplete_date.year == year
    assert parsed_incomplete_date.month == month
    assert parsed_incomplete_date.day == 1  # Default day

    # Parse the generated datetime string and check properties.
    parsed_dt = isoparse(dt_str)

    # Check if the parsed components match the generated ones.
    assert parsed_dt.year == year
    assert parsed_dt.month == month
    assert parsed_dt.day == day
    assert parsed_dt.hour == hour
    assert parsed_dt.minute == minute
    assert parsed_dt.second == second
    assert parsed_dt.microsecond == microsecond

    # Check if the time zone is parsed correctly.
    if include_timezone:
        assert parsed_dt.tzinfo.utcoffset(parsed_dt) == datetime.timedelta(hours=timezone_hour_offset, minutes=timezone_minute_offset)
    else:
        assert parsed_dt.tzinfo.utcoffset(parsed_dt) is None  # UTC has no offset

# End program