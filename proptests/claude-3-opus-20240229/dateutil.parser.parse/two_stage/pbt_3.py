from hypothesis import given, strategies as st
from dateutil.parser import parse
from datetime import datetime

@given(st.dates(), st.times())
def test_parse_unambiguous_datetime(date, time):
    datestr = f"{date.isoformat()} {time.isoformat()}"
    parsed = parse(datestr)
    assert parsed.date() == date
    assert parsed.time() == time

@given(st.datetimes(), st.timezones())
def test_parse_tzinfo(dt, tz):
    datestr = dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    parsed = parse(datestr, tzinfos={tz.tzname(dt): tz})
    assert parsed.tzinfo == tz

@given(st.datetimes())
def test_parse_ignoretz(dt):
    datestr = dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    parsed = parse(datestr, ignoretz=True)
    assert parsed.tzinfo is None

@given(st.datetimes(), st.datetimes())
def test_parse_default(default, dt):
    datestr = dt.strftime("%H:%M:%S")
    parsed = parse(datestr, default=default)
    assert parsed.date() == default.date()
    assert parsed.time() == dt.time()

@given(st.datetimes(), st.text())
def test_parse_fuzzy_with_tokens(dt, fuzz):
    datestr = dt.strftime("%Y-%m-%d") + " " + fuzz
    parsed, tokens = parse(datestr, fuzzy_with_tokens=True)
    assert parsed.date() == dt.date()
    assert fuzz in tokens
# End program