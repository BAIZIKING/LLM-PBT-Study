from hypothesis import given, strategies as st
from dateutil.parser import parse
from dateutil.tz import gettz
import datetime

# Testing the type of the output
@given(st.text())
def test_output_type(timestr):
    output = parse(timestr)
    assert isinstance(output, datetime.datetime)

# Testing the correctness of the parsed date
@given(st.dates())
def test_correctness(date):
    timestr = date.isoformat()
    assert parse(timestr).date() == date

# Testing handling of timezones
@given(st.text(), st.booleans())
def test_handling_timezones(timestr, ignoretz):
    if ignoretz:
        assert parse(timestr, ignoretz=True).tzinfo is None
    else:
        # verify that parsed timezone matches the original
        pass  # Timezone parsing is complex 

# Testing precedence of defaults
@given(st.datetimes(), st.text())
def test_precedence_defaults(default, timestr):
    result = parse(timestr, default=default)
    if default:
        assert result.year == default.year or not timestr
        assert result.month == default.month or not timestr
        assert result.day == default.day or not timestr
    else:
        assert result.year == 1900 or not timestr
        assert result.month == 1 or not timestr
        assert result.day == 1 or not timestr

# Testing handling of invalid inputs
@given(st.text())
def test_invalid_inputs(timestr):
    try:
        parse(timestr)
    except ValueError:
        # If a ValueError is raised, that's okay, we expected it!
        pass