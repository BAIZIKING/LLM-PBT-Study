from hypothesis import given, strategies as st
from datetime import datetime

@given(st.floats(min_value=0, max_value=2147483647), 
       st.one_of(st.none(), st.datetimes().map(lambda d: d.tzinfo)))
def test_datetime_fromtimestamp(timestamp, tz):
    dt = datetime.fromtimestamp(timestamp, tz)
    # Assert that we get a datetime object
    assert isinstance(dt, datetime)
    # Assert year in expected range if timestamp is in supported range
    assert 1970 <= dt.year <= 2038