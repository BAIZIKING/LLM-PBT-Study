from hypothesis import given, strategies as st
from datetime import datetime
import dateutil.parser
import dateutil.tz

@given(st.datetimes(min_value=datetime(1, 1, 1), max_value=datetime(9999, 12, 31, 23, 59, 59, 999999)))
def test_isoparse_returns_datetime(dt):
    iso_str = dt.isoformat()
    parsed_dt = dateutil.parser.isoparse(iso_str)
    assert isinstance(parsed_dt, datetime)

@given(st.datetimes(min_value=datetime(1, 1, 1), max_value=datetime(9999, 12, 31)))
def test_isoparse_date_components(dt):
    iso_str = dt.date().isoformat()
    parsed_dt = dateutil.parser.isoparse(iso_str)
    assert parsed_dt.year == dt.year
    assert parsed_dt.month == dt.month
    assert parsed_dt.day == dt.day

@given(st.datetimes(min_value=datetime(1, 1, 1), max_value=datetime(9999, 12, 31, 23, 59, 59, 999999)))
def test_isoparse_time_components(dt):
    iso_str = dt.time().isoformat()
    parsed_dt = dateutil.parser.isoparse(iso_str)
    assert parsed_dt.hour == dt.hour
    assert parsed_dt.minute == dt.minute
    assert parsed_dt.second == dt.second
    assert parsed_dt.microsecond == dt.microsecond

@given(st.datetimes(min_value=datetime(1, 1, 1), max_value=datetime(9999, 12, 31, 23, 59, 59, 999999)))
def test_isoparse_no_tzinfo(dt):
    iso_str = dt.isoformat()
    parsed_dt = dateutil.parser.isoparse(iso_str)
    assert parsed_dt.tzinfo is None

@given(st.datetimes(min_value=datetime(1, 1, 1), max_value=datetime(9999, 12, 31, 23, 59, 59, 999999), timezones=st.just(dateutil.tz.tzutc())))
def test_isoparse_with_tzinfo(dt):
    iso_str = dt.isoformat()
    parsed_dt = dateutil.parser.isoparse(iso_str)
    assert isinstance(parsed_dt.tzinfo, (dateutil.tz.tzoffset, dateutil.tz.tzutc))

# End program