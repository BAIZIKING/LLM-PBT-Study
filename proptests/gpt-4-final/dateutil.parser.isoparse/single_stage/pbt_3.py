from hypothesis import given, strategies as st
from dateutil.parser import isoparse
from datetime import datetime


# Generate datetime strings in different formats
def datetime_string(min_year=1000, max_year=9999):
    return st.builds(
        "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}{:s}{:02d}:{:02d}".format,
        st.integers(min_year, max_year),  # Year
        st.integers(1, 12),  # Month
        st.integers(1, 28),  # Day, up to 28 to avoid month/year issues
        st.integers(0, 23),  # Hour
        st.integers(0, 59),  # Minute
        st.integers(0, 59),  # Second
        st.sampled_from(['+', '-', 'Z']),  # Time zone direction or 'Z' for UTC
        st.integers(0, 23),  # Time zone hours
        st.integers(0, 59)  # Time zone minutes
    )


@given(st.data())
def test_dateutil_parser_isoparse(data):
    dt_string = data.draw(datetime_string())
    dt = isoparse(dt_string)
    # This is a valid datetime, so it should parse successfully
    assert isinstance(dt, datetime)
    # Unspecified components should default to their lowest value
    assert dt.year >= 1000
    assert dt.month >= 1
    assert dt.day >= 1
    assert dt.hour >= 0
    assert dt.minute >= 0
    assert dt.second >= 0
# End program