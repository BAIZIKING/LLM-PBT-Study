from hypothesis import given, strategies as st
from dateutil.parser import isoparse
from datetime import datetime

# Summary: 
# Generate a variety of valid ISO 8601 datetime strings, including:
# - Dates only (YYYY, YYYY-MM, YYYY-MM-DD) 
# - Dates with times (adding T separator and HH, HH:MM, or HH:MM:SS)
# - Dates with times and timezone offsets (Z, ±HH:MM, ±HHMM, ±HH)
# Also generate some invalid strings to check that exceptions are raised.
@given(st.one_of(
    st.dates().map(lambda d: d.isoformat()),
    st.datetimes().map(lambda dt: dt.isoformat()),
    st.datetimes().map(lambda dt: dt.isoformat() + "Z"),
    st.datetimes().map(lambda dt: dt.isoformat() + "+01:00"), 
    st.datetimes().map(lambda dt: dt.isoformat() + "-0100"),
    st.datetimes().map(lambda dt: dt.isoformat() + "+01"),
    st.from_regex(r"\d{4}(-\d{2}){0,2}(T\d{2}(:\d{2}){0,2}(\.\d{1,6})?([-+](\d{2}:?\d{2}|Z))?)?", fullmatch=True),
    st.from_regex(r"\d{4}W\d{2}(-\d)?", fullmatch=True),
    st.text()
))
def test_isoparse(dt_str):
    try:
        # Check that isoparse either returns a valid datetime or raises ValueError
        dt = isoparse(dt_str)
        assert isinstance(dt, datetime)
        assert dt_str == dt.isoformat()
    except ValueError:
        assert not isinstance(dt_str, str) or not (
            dt_str.startswith(tuple(str(i) for i in range(10))) and 
            "T" not in dt_str[5:]
        )
# End program