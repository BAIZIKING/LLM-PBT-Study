from hypothesis import given, strategies as st
from dateutil.parser import parse
from datetime import datetime

@given(st.datetimes())
def test_parse_valid_datetime(dt):
    assert parse(str(dt)) == dt

@given(st.datetimes(), st.booleans())
def test_parse_ignoretz(dt, ignoretz):
    parsed_dt = parse(str(dt), ignoretz=ignoretz)
    if ignoretz:
        assert parsed_dt.tzinfo is None
    else:
        assert parsed_dt.tzinfo is not None

@given(st.datetimes(), st.datetimes())
def test_parse_default(default_dt, dt):
    parsed_dt = parse(str(dt), default=default_dt)
    for attr in ['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond']:
        if getattr(dt, attr) == getattr(default_dt, attr):
            assert getattr(parsed_dt, attr) == getattr(default_dt, attr)
        else:
            assert getattr(parsed_dt, attr) == getattr(dt, attr)

@given(st.dates().map(lambda d: '{}/{}/{}'.format(d.month, d.day, d.year % 100)),
       st.booleans(), st.booleans())
def test_parse_yearfirst(date_str, yearfirst, dayfirst):
    parsed_dt = parse(date_str, yearfirst=yearfirst, dayfirst=dayfirst)
    if yearfirst:
        assert parsed_dt.year == int(date_str.split('/')[-1]) + 2000
    else:
        assert parsed_dt.year == datetime.now().year

@given(st.text(), st.booleans())
def test_parse_fuzzy_with_tokens(timestr, fuzzy_with_tokens):
    parsed_result = parse(timestr, fuzzy_with_tokens=fuzzy_with_tokens)
    if fuzzy_with_tokens:
        assert isinstance(parsed_result, tuple)
        assert isinstance(parsed_result[0], datetime)
        assert isinstance(parsed_result[1], tuple)
    else:
        assert isinstance(parsed_result, datetime)
# End program