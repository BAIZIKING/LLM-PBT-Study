from hypothesis import given, strategies as st
from dateutil.parser import parse
from datetime import datetime

@given(st.datetimes())
def test_parsed_datetime_matches_input(dt):
    assert parse(str(dt)) == dt

@given(st.datetimes(), st.datetimes())
def test_default_parameter(default_dt, input_dt):
    parsed_dt = parse(str(input_dt.date()), default=default_dt)
    assert parsed_dt.date() == input_dt.date()
    assert parsed_dt.time() == default_dt.time()

@given(st.datetimes(timezones=st.timezones()))
def test_ignoretz_parameter(dt):
    parsed_dt = parse(str(dt), ignoretz=True)
    assert parsed_dt.tzinfo is None

@given(st.datetimes(timezones=st.timezones()), st.dictionaries(st.text(), st.timezones()))
def test_tzinfos_parameter(dt, tzinfos):
    parsed_dt = parse(str(dt).replace(str(dt.tzname()), list(tzinfos.keys())[0]), tzinfos=tzinfos)
    assert parsed_dt.tzinfo == list(tzinfos.values())[0]

@given(st.text())
def test_fuzzy_with_tokens_parameter(timestr):
    parsed_result = parse(timestr, fuzzy_with_tokens=True)
    assert isinstance(parsed_result, tuple)
    assert isinstance(parsed_result[0], datetime)
    assert isinstance(parsed_result[1], tuple)
# End program