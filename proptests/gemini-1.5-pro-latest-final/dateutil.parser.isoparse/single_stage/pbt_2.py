from hypothesis import given, strategies as st
from dateutil.parser import isoparse
import datetime

# Summary: Generate random date and time strings adhering to ISO-8601 format, considering various supported formats and edge cases.
@given(st.data())
def test_dateutil_parser_isoparse(data):
    # Generate year, month, day, hour, minute, second, and microsecond components
    year = data.draw(st.integers(min_value=1, max_value=9999))
    month = data.draw(st.integers(min_value=1, max_value=12))
    day = data.draw(st.integers(min_value=1, max_value=28))  # Keep day within a safe range to avoid invalid dates
    hour = data.draw(st.integers(min_value=0, max_value=23))
    minute = data.draw(st.integers(min_value=0, max_value=59))
    second = data.draw(st.integers(min_value=0, max_value=59))
    microsecond = data.draw(st.integers(min_value=0, max_value=999999))

    # Construct date and time strings
    date_str = f"{year:04}-{month:02}-{day:02}"
    time_str = f"{hour:02}:{minute:02}:{second:02}.{microsecond:06}"

    # Randomly choose to include or exclude time portion
    include_time = data.draw(st.booleans())
    if include_time:
        dt_str = date_str + "T" + time_str
    else:
        dt_str = date_str

    # Parse the generated string
    try:
        parsed_datetime = isoparse(dt_str)

        # Check properties based on API documentation:
        # 1. Parsed object is a datetime.datetime instance
        assert isinstance(parsed_datetime, datetime.datetime)

        # 2. Year, month, and day match the generated values
        assert parsed_datetime.year == year
        assert parsed_datetime.month == month
        assert parsed_datetime.day == day

        # 3. If time was included, hour, minute, second, and microsecond match
        if include_time:
            assert parsed_datetime.hour == hour
            assert parsed_datetime.minute == minute
            assert parsed_datetime.second == second
            assert parsed_datetime.microsecond == microsecond
    except ValueError:
        # If parsing fails, ensure it's due to an invalid date (day exceeding month's limit)
        assert month in [2, 4, 6, 9, 11] and day > 28

# End program