from hypothesis import given, strategies as st
from datetime import datetime
import dateutil.parser
import dateutil.tz

@given(st.datetimes())
def test_return_type(dt):
    iso_str = dt.isoformat()
    parsed_dt = dateutil.parser.isoparse(iso_str)
    assert isinstance(parsed_dt, datetime)

@given(st.datetimes())
def test_time_equivalence(dt):
    iso_str = dt.isoformat()
    parsed_dt = dateutil.parser.isoparse(iso_str)
    assert dt == parsed_dt

@given(st.datetimes(timezones=None))
def test_naive_datetime(dt):
    iso_str = dt.isoformat()
    parsed_dt = dateutil.parser.isoparse(iso_str)
    assert parsed_dt.tzinfo is None

@given(st.datetimes(timezones=st.just(dateutil.tz.UTC)))
def test_tzinfo_utc(dt):
    iso_str = dt.isoformat()
    parsed_dt = dateutil.parser.isoparse(iso_str)
    assert parsed_dt.tzinfo == dateutil.tz.UTC

@given(st.text())
def test_invalid_iso_string(invalid_str):
    try:
        dateutil.parser.isoparse(invalid_str)
    except ValueError:
        assert True
    else:
        assert False
# End program