from hypothesis import given, strategies as st
import dateutil.parser
import datetime
import dateutil.tz

@given(st.datetimes(min_value=datetime.datetime(1, 1, 1), max_value=datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)))
def test_return_type(dt):
    iso_str = dt.isoformat()
    parsed_dt = dateutil.parser.isoparse(iso_str)
    assert isinstance(parsed_dt, datetime.datetime)

@given(st.datetimes(min_value=datetime.datetime(1, 1, 1), max_value=datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)))
def test_roundtrip(dt):
    iso_str = dt.isoformat()
    parsed_dt = dateutil.parser.isoparse(iso_str)
    assert parsed_dt == dt

@given(st.datetimes(min_value=datetime.datetime(1, 1, 1), max_value=datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)))
def test_components(dt):
    iso_str = dt.isoformat()
    parsed_dt = dateutil.parser.isoparse(iso_str)
    assert parsed_dt.year == dt.year
    assert parsed_dt.month == dt.month
    assert parsed_dt.day == dt.day
    assert parsed_dt.hour == dt.hour
    assert parsed_dt.minute == dt.minute
    assert parsed_dt.second == dt.second
    assert parsed_dt.microsecond == dt.microsecond

@given(st.datetimes(min_value=datetime.datetime(1, 1, 1), max_value=datetime.datetime(9999, 12, 31, 23, 59, 59, 999999), timezones=st.just(dateutil.tz.tzutc())))
def test_tzinfo_utc(dt):
    iso_str = dt.isoformat()
    parsed_dt = dateutil.parser.isoparse(iso_str)
    assert parsed_dt.tzinfo == dateutil.tz.tzutc()

@given(st.dates(min_value=datetime.date(1, 1, 1), max_value=datetime.date(9999, 12, 31)))
def test_default_lowest(d):
    iso_str = d.isoformat()
    parsed_dt = dateutil.parser.isoparse(iso_str)
    assert parsed_dt.hour == 0
    assert parsed_dt.minute == 0
    assert parsed_dt.second == 0
    assert parsed_dt.microsecond == 0
# End program