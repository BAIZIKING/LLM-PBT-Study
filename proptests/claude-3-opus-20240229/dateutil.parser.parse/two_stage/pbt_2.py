from hypothesis import given, strategies as st
from dateutil.parser import parse
import datetime

@given(st.datetimes(), st.booleans())
def test_return_type(dt, fuzzy_with_tokens):
    if fuzzy_with_tokens:
        parsed_result = parse(str(dt), fuzzy_with_tokens=True)
        assert isinstance(parsed_result, tuple)
        assert isinstance(parsed_result[0], datetime.datetime)
    else:
        parsed_result = parse(str(dt))
        assert isinstance(parsed_result, datetime.datetime)

@given(st.datetimes(timezones=st.timezones()), st.booleans())
def test_timezone_awareness(dt, ignoretz):
    parsed_result = parse(str(dt), ignoretz=ignoretz)
    if ignoretz:
        assert parsed_result.tzinfo is None
    else:
        assert parsed_result.tzinfo is not None

@given(st.datetimes(), st.datetimes())
def test_default_values(default_dt, dt):
    input_str = dt.strftime("%Y-%m-%d")
    parsed_result = parse(input_str, default=default_dt)
    assert parsed_result.time() == default_dt.time()

@given(st.datetimes(), st.booleans())
def test_yearfirst(dt, yearfirst):
    input_str = dt.strftime("%d-%m-%y")
    parsed_result = parse(input_str, yearfirst=yearfirst)
    if yearfirst:
        assert parsed_result.year == dt.year % 100
    else:
        assert parsed_result.year == dt.year % 100 + 2000

@given(st.timezones(), st.datetimes())
def test_tzinfos(tzinfo, dt):
    tzname = tzinfo.tzname(dt)
    input_str = f"{dt.strftime('%Y-%m-%d %H:%M:%S')} {tzname}"
    parsed_result = parse(input_str, tzinfos={tzname: tzinfo})
    assert parsed_result.tzinfo == tzinfo
# End program