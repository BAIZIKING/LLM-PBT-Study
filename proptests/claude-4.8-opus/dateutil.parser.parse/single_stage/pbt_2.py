from hypothesis import given, strategies as st
import datetime

from dateutil.parser import parse

# Summary: Generate random naive datetimes, serialize them to date/time strings
# that dateutil understands (using multiple unambiguous formats and optional
# fuzzy filler text), then verify round-trip equality, correct return types,
# fuzzy parsing behavior, fuzzy_with_tokens tuple shape, and ignoretz invariance.
@given(st.data())
def test_dateutil_parser_parse():
    data = st.data()  # placeholder, real draws below

    # Draw a naive datetime within a safe range (avoid OverflowError edge cases
    # by staying well inside C-int year bounds).
    dt = data.draw(
        st.datetimes(
            min_value=datetime.datetime(1, 1, 1),
            max_value=datetime.datetime(9999, 12, 31, 23, 59, 59),
        )
    )

    # Choose a formatting style. Some styles drop microseconds, so we track the
    # expected (rounded) datetime accordingly.
    style = data.draw(st.sampled_from(["iso_full", "iso_no_micro", "space_sep"]))

    if style == "iso_full":
        date_str = dt.isoformat()
        expected = dt
    elif style == "iso_no_micro":
        expected = dt.replace(microsecond=0)
        date_str = expected.isoformat()
    else:  # space_sep
        expected = dt.replace(microsecond=0)
        date_str = expected.strftime("%Y-%m-%d %H:%M:%S")

    # Property 1: Basic round-trip. parse() must return a datetime.datetime
    # equal to the original (within the formatted precision).
    result = parse(date_str)
    assert isinstance(result, datetime.datetime)
    assert result == expected

    # Property 4: ignoretz invariance. Our strings carry no timezone info,
    # so ignoretz=True must not change the result.
    result_ignoretz = parse(date_str, ignoretz=True)
    assert isinstance(result_ignoretz, datetime.datetime)
    assert result_ignoretz == expected

    # Property 2 & 3: Fuzzy parsing with surrounding filler text.
    prefix = data.draw(st.sampled_from(["", "Today is ", "The event on "]))
    suffix = data.draw(st.sampled_from(["", " happened", " was scheduled"]))
    fuzzy_str = f"{prefix}{date_str}{suffix}"

    fuzzy_result = parse(fuzzy_str, fuzzy=True)
    assert isinstance(fuzzy_result, datetime.datetime)
    assert fuzzy_result == expected

    # fuzzy_with_tokens must return a (datetime, tuple-of-str) pair.
    fwt_result = parse(fuzzy_str, fuzzy_with_tokens=True)
    assert isinstance(fwt_result, tuple)
    assert len(fwt_result) == 2
    parsed_dt, tokens = fwt_result
    assert isinstance(parsed_dt, datetime.datetime)
    assert parsed_dt == expected
    assert isinstance(tokens, tuple)
    assert all(isinstance(tok, str) for tok in tokens)
# End program