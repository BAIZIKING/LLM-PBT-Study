from hypothesis import given, strategies as st
from datetime import datetime, timedelta
from dateutil.parser import isoparse
from dateutil.tz import tzoffset, tzutc

@given(st.dates().map(lambda d: d.isoformat()))
def test_isoparse_returns_datetime(dt_str):
    dt = isoparse(dt_str)
    assert isinstance(dt, datetime)

@given(st.datetimes().map(lambda dt: dt.isoformat()))
def test_isoparse_valid_string(dt_str):
    try:
        isoparse(dt_str)
    except ValueError:
        assert False, f"Unexpected ValueError for valid string: {dt_str}"

@given(st.dates().map(lambda d: d.isoformat()))
def test_isoparse_date_components(dt_str):
    dt = isoparse(dt_str)
    expected_date = datetime.strptime(dt_str, "%Y-%m-%d").date()
    assert dt.year == expected_date.year
    assert dt.month == expected_date.month
    assert dt.day == expected_date.day

@given(st.datetimes().map(lambda dt: dt.isoformat()))
def test_isoparse_time_components(dt_str):
    dt = isoparse(dt_str)
    expected_time = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%f")
    assert dt.hour == expected_time.hour
    assert dt.minute == expected_time.minute
    assert dt.second == expected_time.second
    assert dt.microsecond == expected_time.microsecond

@given(st.datetimes(timezones=st.just(timedelta(hours=-12))).map(lambda dt: dt.isoformat()))
def test_isoparse_timezone(dt_str):
    dt = isoparse(dt_str)
    expected_offset = timedelta(hours=-12)
    if str(expected_offset) in dt_str:
        assert isinstance(dt.tzinfo, tzoffset)
        assert dt.utcoffset() == expected_offset
    else:
        assert dt.tzinfo is None

@given(st.datetimes(timezones=st.just(timedelta(0))).map(lambda dt: dt.isoformat()))
def test_isoparse_utc_timezone(dt_str):
    dt = isoparse(dt_str)
    assert dt.tzinfo == tzutc()
# End program