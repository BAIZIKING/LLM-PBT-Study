from hypothesis import given, strategies as st
from hypothesis.strategies import dates, times, none
from datetime import datetime
from dateutil.parser import isoparse

@given(
    st.dates(min_value=datetime(1, 1, 1).date(), max_value=datetime(9999, 12, 31).date()),
    st.times().filter(lambda x: x.second == int(x.second)),
    st.sampled_from(["Z", "+HH:MM", "+HHMM", "+HH", none()]),
)
def test_isoparse(date, time, tz):
    iso_format = f"%Y-%m-%dT%H:%M:%S{tz}" if tz else "%Y-%m-%dT%H:%M:%S"
    dt_str = datetime.combine(date, time).strftime(iso_format)
    parsed_dt = isoparse(dt_str)

    assert parsed_dt.year == date.year
    assert parsed_dt.month == date.month
    assert parsed_dt.day == date.day
    assert parsed_dt.hour == time.hour
    assert parsed_dt.minute == time.minute
    assert parsed_dt.second == time.second

    if not tz:
        assert parsed_dt.tzinfo is None