from hypothesis import given, strategies as st
import dateutil
import dateutil.parser
from datetime import datetime


BOUNDED_NAIVE_DATETIMES = st.datetimes(
    min_value=datetime(1900, 1, 1, 0, 0, 0),
    max_value=datetime(2099, 12, 31, 23, 59, 59),
    timezones=st.none(),
)


@given(st.data())
def test_dateutil_parser_parse_returns_datetime_when_not_fuzzy_with_tokens(data):
    dt = data.draw(BOUNDED_NAIVE_DATETIMES)
    timestr = dt.isoformat(sep=" ")

    result = dateutil.parser.parse(timestr, fuzzy_with_tokens=False)

    assert isinstance(result, datetime)


@given(st.data())
def test_dateutil_parser_parse_fuzzy_with_tokens_returns_datetime_and_tokens(data):
    dt = data.draw(BOUNDED_NAIVE_DATETIMES)
    prefix = data.draw(st.sampled_from(["Today is ", "Report generated at ", "Timestamp: "]))
    suffix = data.draw(st.sampled_from(["", " done", " UTC ignored text"]))
    timestr = prefix + dt.isoformat(sep=" ") + suffix

    result = dateutil.parser.parse(timestr, fuzzy_with_tokens=True)

    assert isinstance(result, tuple)
    assert len(result) == 2
    parsed_dt, ignored_tokens = result
    assert isinstance(parsed_dt, datetime)
    assert isinstance(ignored_tokens, tuple)
    assert all(isinstance(token, str) for token in ignored_tokens)


@given(st.data())
def test_dateutil_parser_parse_ignoretz_returns_naive_datetime(data):
    dt = data.draw(BOUNDED_NAIVE_DATETIMES)
    sign = data.draw(st.sampled_from(["+", "-"]))
    offset_hour = data.draw(st.integers(min_value=0, max_value=14))
    offset_minute = data.draw(st.integers(min_value=0, max_value=59))
    tz_offset = f"{sign}{offset_hour:02d}{offset_minute:02d}"
    timestr = dt.strftime("%Y-%m-%d %H:%M:%S") + " " + tz_offset

    result = dateutil.parser.parse(timestr, ignoretz=True)

    assert isinstance(result, datetime)
    assert result.tzinfo is None


@given(st.data())
def test_dateutil_parser_parse_uses_default_for_unspecified_fields(data):
    default = data.draw(BOUNDED_NAIVE_DATETIMES)
    hour = data.draw(st.integers(min_value=0, max_value=23))
    minute = data.draw(st.integers(min_value=0, max_value=59))
    second = data.draw(st.integers(min_value=0, max_value=59))
    timestr = f"{hour:02d}:{minute:02d}:{second:02d}"

    result = dateutil.parser.parse(timestr, default=default)

    assert result.year == default.year
    assert result.month == default.month
    assert result.day == default.day
    assert result.hour == hour
    assert result.minute == minute
    assert result.second == second
    assert result.microsecond == default.microsecond


@given(st.data())
def test_dateutil_parser_parse_ambiguous_date_respects_dayfirst_and_yearfirst(data):
    dayfirst = data.draw(st.booleans())
    yearfirst = data.draw(st.booleans())
    timestr = "01/05/09"

    result = dateutil.parser.parse(
        timestr,
        dayfirst=dayfirst,
        yearfirst=yearfirst,
    )

    parser_info = dateutil.parser.parserinfo()

    if yearfirst:
        expected_year = parser_info.convertyear(1)
        if dayfirst:
            expected_month = 9
            expected_day = 5
        else:
            expected_month = 5
            expected_day = 9
    else:
        expected_year = parser_info.convertyear(9)
        if dayfirst:
            expected_month = 5
            expected_day = 1
        else:
            expected_month = 1
            expected_day = 5

    assert result.year == expected_year
    assert result.month == expected_month
    assert result.day == expected_day
# End program