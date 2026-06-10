from hypothesis import given, strategies as st
from dateutil.parser import parse
from dateutil.tz import tzoffset
import datetime

@given(st.dates(), st.times(), st.timezones())
def test_correct_datetime_values(date, time, tz):
    datetime_str = f"{date.isoformat()} {time.isoformat()}"
    parsed_datetime = parse(datetime_str, ignoretz=False)
    assert parsed_datetime.date() == date
    assert parsed_datetime.time().replace(microsecond=0) == time.replace(microsecond=0)
    assert parsed_datetime.tzinfo == tz

@given(st.datetimes(timezones=st.just(None)), st.booleans())
def test_ignoretz(dt, ignoretz):
    datetime_str = dt.isoformat()
    parsed_datetime = parse(datetime_str, ignoretz=ignoretz)
    if ignoretz:
        assert parsed_datetime.tzinfo is None
    else:
        assert parsed_datetime.tzinfo is not None

@given(st.datetimes(timezones=st.just(None)), st.datetimes(timezones=st.just(None)))
def test_default(default_dt, dt):
    datetime_str = dt.strftime("%Y-%m-%d")
    parsed_datetime = parse(datetime_str, default=default_dt)
    assert parsed_datetime.time() == default_dt.time()

@given(st.integers(min_value=1, max_value=31), st.integers(min_value=1, max_value=12), st.integers(min_value=1000, max_value=9999), st.booleans(), st.booleans())
def test_yearfirst_dayfirst(day, month, year, yearfirst, dayfirst):
    datetime_str = f"{month:02d}/{day:02d}/{year}"
    parsed_datetime = parse(datetime_str, yearfirst=yearfirst, dayfirst=dayfirst)
    if yearfirst:
        assert parsed_datetime.year == year
        if dayfirst:
            assert parsed_datetime.month == day
            assert parsed_datetime.day == month
        else:
            assert parsed_datetime.month == month
            assert parsed_datetime.day == day
    else:
        assert parsed_datetime.day == day
        assert parsed_datetime.month == month
        assert parsed_datetime.year == year

@given(st.datetimes(timezones=st.just(None)), st.booleans())
def test_fuzzy_with_tokens(dt, fuzzy_with_tokens):
    datetime_str = f"Today is {dt.strftime('%B %d, %Y at %I:%M%p')}"
    if fuzzy_with_tokens:
        parsed_result = parse(datetime_str, fuzzy_with_tokens=True)
        assert isinstance(parsed_result, tuple)
        assert parsed_result[0] == dt
        assert isinstance(parsed_result[1], tuple)
    else:
        parsed_datetime = parse(datetime_str, fuzzy_with_tokens=False)
        assert parsed_datetime == dt
# End program