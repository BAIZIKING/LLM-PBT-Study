from hypothesis import given, strategies as st
import dateutil
import dateutil.parser
import datetime

@given(st.data())
def test_dateutil_parser_parse_returns_datetime_without_fuzzy_tokens(data):
    dt = data.draw(
        st.datetimes(
            min_value=datetime.datetime(1900, 1, 1),
            max_value=datetime.datetime(2099, 12, 31, 23, 59, 59),
        )
    )
    timestr = (
        f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d} "
        f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
    )

    parsed = dateutil.parser.parse(timestr)

    assert isinstance(parsed, datetime.datetime)


@given(st.data())
def test_dateutil_parser_parse_fuzzy_with_tokens_returns_expected_tuple(data):
    dt = data.draw(
        st.datetimes(
            min_value=datetime.datetime(1900, 1, 1),
            max_value=datetime.datetime(2099, 12, 31, 23, 59, 59),
        )
    )
    timestr = (
        f"Today is {dt.year:04d}-{dt.month:02d}-{dt.day:02d} "
        f"at {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d} exactly"
    )

    parsed = dateutil.parser.parse(timestr, fuzzy_with_tokens=True)

    assert isinstance(parsed, tuple)
    assert len(parsed) == 2
    assert isinstance(parsed[0], datetime.datetime)
    assert isinstance(parsed[1], tuple)
    assert all(isinstance(token, str) for token in parsed[1])


@given(st.data())
def test_dateutil_parser_parse_ignoretz_returns_naive_datetime(data):
    dt = data.draw(
        st.datetimes(
            min_value=datetime.datetime(1900, 1, 1),
            max_value=datetime.datetime(2099, 12, 31, 23, 59, 59),
        )
    )
    total_offset_minutes = data.draw(st.integers(min_value=-12 * 60, max_value=14 * 60))
    sign = "+" if total_offset_minutes >= 0 else "-"
    absolute_offset = abs(total_offset_minutes)
    offset_hours, offset_minutes = divmod(absolute_offset, 60)
    offset = f"{sign}{offset_hours:02d}{offset_minutes:02d}"
    timestr = (
        f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d} "
        f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d} {offset}"
    )

    parsed = dateutil.parser.parse(
        timestr,
        ignoretz=True,
        tzinfos={"UTC": datetime.timezone.utc},
    )

    assert isinstance(parsed, datetime.datetime)
    assert parsed.tzinfo is None


@given(st.data())
def test_dateutil_parser_parse_default_supplies_unspecified_fields(data):
    default = data.draw(
        st.datetimes(
            min_value=datetime.datetime(1900, 1, 1),
            max_value=datetime.datetime(2099, 12, 31, 23, 59, 59),
        )
    ).replace(microsecond=0)
    hour = data.draw(st.integers(min_value=0, max_value=23))
    minute = data.draw(st.integers(min_value=0, max_value=59))
    second = data.draw(st.integers(min_value=0, max_value=59))
    timestr = f"{hour:02d}:{minute:02d}:{second:02d}"

    parsed = dateutil.parser.parse(timestr, default=default)

    assert parsed.year == default.year
    assert parsed.month == default.month
    assert parsed.day == default.day
    assert parsed.hour == hour
    assert parsed.minute == minute
    assert parsed.second == second
    assert parsed.microsecond == default.microsecond


@given(st.data())
def test_dateutil_parser_parse_ambiguous_three_integer_dates_follow_flags(data):
    year_value = data.draw(st.integers(min_value=1, max_value=31))
    first_non_year_value = data.draw(st.integers(min_value=1, max_value=12))
    second_non_year_value = data.draw(st.integers(min_value=1, max_value=12))
    yearfirst = data.draw(st.booleans())
    dayfirst = data.draw(st.booleans())

    if yearfirst:
        timestr = (
            f"{year_value:02d}/"
            f"{first_non_year_value:02d}/"
            f"{second_non_year_value:02d}"
        )
    else:
        timestr = (
            f"{first_non_year_value:02d}/"
            f"{second_non_year_value:02d}/"
            f"{year_value:02d}"
        )

    if dayfirst:
        expected_day = first_non_year_value
        expected_month = second_non_year_value
    else:
        expected_month = first_non_year_value
        expected_day = second_non_year_value

    parsed = dateutil.parser.parse(
        timestr,
        yearfirst=yearfirst,
        dayfirst=dayfirst,
        default=datetime.datetime(2000, 1, 1),
    )

    assert parsed.month == expected_month
    assert parsed.day == expected_day

# End program