from hypothesis import given, strategies as st
import datetime
from dateutil.parser import parse, ParserError

# Summary: Generate known naive datetimes and serialize them with an unambiguous
# ISO-like strftime format, then vary kwargs (ignoretz, fuzzy_with_tokens,
# dayfirst, yearfirst, default). We verify: round-trip equality of components on
# unambiguous strings, correct return type for fuzzy_with_tokens, that ignoretz
# yields a naive datetime, and that only documented exceptions are raised.
@given(st.data())
def test_dateutil_parser_parse(data):
    dt = data.draw(st.datetimes(
        min_value=datetime.datetime(1900, 1, 1),
        max_value=datetime.datetime(2999, 12, 31, 23, 59, 59),
    ))

    # Unambiguous format so dayfirst/yearfirst cannot reinterpret fields.
    fmt = data.draw(st.sampled_from([
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]))
    timestr = dt.strftime(fmt)

    ignoretz = data.draw(st.booleans())
    fuzzy_with_tokens = data.draw(st.booleans())
    dayfirst = data.draw(st.sampled_from([None, True, False]))
    yearfirst = data.draw(st.sampled_from([None, True, False]))
    use_default = data.draw(st.booleans())
    default = data.draw(st.datetimes()) if use_default else None

    try:
        result = parse(
            timestr,
            ignoretz=ignoretz,
            fuzzy_with_tokens=fuzzy_with_tokens,
            dayfirst=dayfirst,
            yearfirst=yearfirst,
            default=default,
        )
    except (ParserError, OverflowError, ValueError):
        # Only documented (plus underlying ValueError) exceptions allowed.
        return

    # Property: return type depends on fuzzy_with_tokens.
    if fuzzy_with_tokens:
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], datetime.datetime)
        assert isinstance(result[1], tuple)
        parsed = result[0]
    else:
        assert isinstance(result, datetime.datetime)
        parsed = result

    # Property: ignoretz=True always yields a naive datetime.
    if ignoretz:
        assert parsed.tzinfo is None

    # Property: round-trip correctness on unambiguous input.
    # The datetime fields present in the format string must match the original.
    assert parsed.year == dt.year
    assert parsed.month == dt.month
    assert parsed.day == dt.day
    if "%H" in fmt:
        assert parsed.hour == dt.hour
    if "%M" in fmt:
        assert parsed.minute == dt.minute
    if "%S" in fmt:
        assert parsed.second == dt.second
# End program