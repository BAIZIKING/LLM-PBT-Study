from hypothesis import given, strategies as st
from dateutil.parser import isoparse
import datetime

# Summary: This strategy generates random ISO 8601 datetime strings, covering various date, time, and time zone offset formats. 
# It aims to create a wide variety of inputs, including edge cases, to thoroughly test the isoparse function.
@given(st.data())
def test_dateutil_parser_isoparse(data):
    # Generate date components
    year = data.draw(st.integers(min_value=1, max_value=9999))
    month = data.draw(st.integers(min_value=1, max_value=12))
    day = data.draw(st.integers(min_value=1, max_value=28))  # Keep it simple to avoid invalid dates

    # Generate time components
    hour = data.draw(st.integers(min_value=0, max_value=23))
    minute = data.draw(st.integers(min_value=0, max_value=59))
    second = data.draw(st.integers(min_value=0, max_value=59))
    microsecond = data.draw(st.integers(min_value=0, max_value=999999))

    # Generate time zone offset components
    tz_hour_offset = data.draw(st.integers(min_value=-12, max_value=14))
    tz_minute_offset = data.draw(st.integers(min_value=0, max_value=59))

    # Construct the datetime string with varying formats
    date_formats = ["%Y", "%Y-%m", "%Y%m", "%Y-%m-%d", "%Y%m%d"]
    time_formats = ["%H", "%H:%M", "%H%M", "%H:%M:%S", "%H%M%S", "%H:%M:%S.%f"]
    tz_formats = ["Z", "+%H:%M", "-%H:%M", "+%H%M", "-%H%M", "+%H", "-%H"]

    date_str = data.draw(st.sampled_from(date_formats)) % (year, month, day)
    time_str = data.draw(st.sampled_from(time_formats)) % (hour, minute, second, microsecond)
    tz_str = data.draw(st.sampled_from(tz_formats)) % (tz_hour_offset, tz_minute_offset)

    dt_str = date_str + "T" + time_str + tz_str

    # Parse the generated datetime string
    parsed_dt = isoparse(dt_str)

    # Check properties based on the API documentation
    assert isinstance(parsed_dt, datetime.datetime)  # Ensure the output is a datetime object
    assert parsed_dt.year == year
    assert parsed_dt.month == month
    assert parsed_dt.day == day
    assert parsed_dt.hour == hour
    assert parsed_dt.minute == minute
    assert parsed_dt.second == second
    assert parsed_dt.microsecond == microsecond

    # Check time zone offset (approximately, as it might be adjusted for DST)
    offset_in_seconds = parsed_dt.utcoffset().total_seconds()
    expected_offset_in_seconds = (tz_hour_offset * 3600) + (tz_minute_offset * 60)
    assert abs(offset_in_seconds - expected_offset_in_seconds) < 3600  # Allow for DST differences

# End program