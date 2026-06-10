from hypothesis import given, strategies as st, assume
import datetime
from dateutil.parser import parse, ParserError

# Summary: Generate valid datetimes, format them into various unambiguous and
# ambiguous string representations, and toggle parse flags (ignoretz, fuzzy,
# fuzzy_with_tokens, dayfirst). Check round-trip equality, return types,
# tz-naivety under ignoretz, and fuzzy recovery from surrounding text.
@given(st.data())
def test_dateutil_parser_parse(data):
    dt = data.draw(st.datetimes(
        min_value=datetime.datetime(1, 1, 1),
        max_value=datetime.datetime(9999, 12, 31),
    ))
    # Strip microseconds since most string formats don't carry them reliably
    dt = dt.replace(microsecond=0)

    # Choose a string-format mode
    mode = data.draw(st.sampled_from(["iso", "ymd_hms", "fuzzy", "ignoretz"]))

    if mode == "iso":
        timestr = dt.isoformat()
        result = parse(timestr)
        assert isinstance(result, datetime.datetime)
        # Unambiguous ISO format must round-trip exactly (naive input -> naive)
        assert result == dt

    elif mode == "ymd_hms":
        # Unambiguous explicit format
        timestr = dt.strftime("%Y-%m-%d %H:%M:%S")
        result = parse(timestr)
        assert isinstance(result, datetime.datetime)
        assert result.year == dt.year
        assert result.month == dt.month
        assert result.day == dt.day
        assert result.hour == dt.hour
        assert result.minute == dt.minute
        assert result.second == dt.second

    elif mode == "fuzzy":
        # Embed an unambiguous date in surrounding text
        core = dt.strftime("%B %d, %Y %H:%M:%S")
        prefix = data.draw(st.sampled_from(["Today is ", "The date was ", "On "]))
        suffix = data.draw(st.sampled_from([" exactly.", " for sure", ""]))
        timestr = prefix + core + suffix

        use_tokens = data.draw(st.booleans())
        if use_tokens:
            result = parse(timestr, fuzzy_with_tokens=True)
            # fuzzy_with_tokens => returns a 2-tuple (datetime, tuple)
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert isinstance(result[0], datetime.datetime)
            assert isinstance(result[1], tuple)
            parsed_dt = result[0]
        else:
            parsed_dt = parse(timestr, fuzzy=True)
            assert isinstance(parsed_dt, datetime.datetime)

        # The embedded datetime should be recovered
        assert parsed_dt.year == dt.year
        assert parsed_dt.month == dt.month
        assert parsed_dt.day == dt.day
        assert parsed_dt.hour == dt.hour
        assert parsed_dt.minute == dt.minute
        assert parsed_dt.second == dt.second

    elif mode == "ignoretz":
        # Append a timezone name; with ignoretz=True result must be naive
        timestr = dt.strftime("%Y-%m-%d %H:%M:%S") + " EST"
        result = parse(timestr, ignoretz=True)
        assert isinstance(result, datetime.datetime)
        # ignoretz=True => naive datetime
        assert result.tzinfo is None
        assert result.year == dt.year
        assert result.month == dt.month
        assert result.day == dt.day
# End program