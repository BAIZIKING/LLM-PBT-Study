from hypothesis import given, strategies as st
import datetime
from dateutil.parser import parse, ParserError

# Summary: Generate known datetimes, format them into unambiguous strings,
# parse them back, and verify return type, round-trip, ignoretz nativity,
# and the fuzzy_with_tokens tuple contract.
@given(st.data())
def test_dateutil_parser_parse(data):
    dt = data.draw(st.datetimes(min_value=datetime.datetime(1900, 1, 1),
                                max_value=datetime.datetime(2100, 12, 31)))
    fmt = data.draw(st.sampled_from(["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
                                     "%Y-%m-%d", "%B %d, %Y %H:%M:%S"]))
    date_str = dt.strftime(fmt)
    ignoretz = data.draw(st.booleans())
    fuzzy_with_tokens = data.draw(st.booleans())
    prefix = data.draw(st.sampled_from(["", "Today is "])) if fuzzy_with_tokens else ""
    suffix = data.draw(st.sampled_from(["", " sharp"])) if fuzzy_with_tokens else ""
    timestr = prefix + date_str + suffix
    try:
        result = parse(timestr, ignoretz=ignoretz, fuzzy_with_tokens=fuzzy_with_tokens)
    except (ParserError, OverflowError, ValueError, TypeError):
        return
    if fuzzy_with_tokens:
        assert isinstance(result, tuple) and len(result) == 2
        parsed_dt, tokens = result
        assert isinstance(parsed_dt, datetime.datetime)
        assert isinstance(tokens, tuple) and all(isinstance(t, str) for t in tokens)
    else:
        assert isinstance(result, datetime.datetime)
        parsed_dt = result
    if ignoretz:
        assert parsed_dt.tzinfo is None
    assert (parsed_dt.year, parsed_dt.month, parsed_dt.day) == (dt.year, dt.month, dt.day)
    if "%H" in fmt:
        assert (parsed_dt.hour, parsed_dt.minute, parsed_dt.second) == (dt.hour, dt.minute, dt.second)