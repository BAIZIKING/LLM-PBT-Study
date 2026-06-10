from hypothesis import given, strategies as st
import dateutil
import dateutil.parser
import datetime as _dt


@given(st.data())
def test_dateutil_parser_parse_returns_datetime_when_successful(data):
    value = data.draw(
        st.datetimes(
            min_value=_dt.datetime(1900, 1, 1),
            max_value=_dt.datetime(2099, 12, 31, 23, 59, 59, 999999),
            timezones=st.none(),
        )
    )
    timestr = value.isoformat(sep=" ")

    result = dateutil.parser.parse(timestr, fuzzy_with_tokens=False)

    assert isinstance(result, _dt.datetime)


@given(st.data())
def test_dateutil_parser_parse_fuzzy_with_tokens_returns_expected_tuple_shape(data):
    value = data.draw(
        st.datetimes(
            min_value=_dt.datetime(1900, 1, 1),
            max_value=_dt.datetime(2099, 12, 31, 23, 59, 59),
            timezones=st.none(),
        )
    )
    timestr = (
        f"Today is {value.year:04d}-{value.month:02d}-{value.day:02d} "
        f"at {value.hour:02d}:{value.minute:02d}:{value.second:02d}"
    )

    result = dateutil.parser.parse(timestr, fuzzy_with_tokens=True)

    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], _dt.datetime)
    assert isinstance(result[1], tuple)
    assert all(isinstance(token, str) for token in result[1])


@given(st.data())
def test_dateutil_parser_parse_ignoretz_returns_naive_datetime(data):
    value = data.draw(
        st.datetimes(
            min_value=_dt.datetime(1900, 1, 1),
            max_value=_dt.datetime(2099, 12, 31, 23, 59, 59),
            timezones=st.none(),
        )
    )
    total_offset_minutes = data.draw(st.integers(min_value=-12 * 60, max_value=12 * 60))
    sign = "+" if total_offset_minutes >= 0 else "-"
    absolute_offset = abs(total_offset_minutes)
    offset_hours, offset_minutes = divmod(absolute_offset, 60)
    timestr = (
        f"{value.year:04d}-{value.month:02d}-{value.day:02d} "
        f"{value.hour:02d}:{value.minute:02d}:{value.second:02d} "
        f"{sign}{offset_hours:02d}:{offset_minutes:02d}"
    )

    result = dateutil.parser.parse(
        timestr,
        ignoretz=True,
        tzinfos={"BRST": -7200, "CST": -21600},
    )

    assert isinstance(result, _dt.datetime)
    assert result.tzinfo is None


@given(st.data())
def test_dateutil_parser_parse_unspecified_fields_are_inherited_from_default(data):
    default = data.draw(
        st.datetimes(
            min_value=_dt.datetime(1900, 1, 1),
            max_value=_dt.datetime(2099, 12, 31, 23, 59, 59, 999999),
            timezones=st.none(),
        )
    )
    hour = data.draw(st.integers(min_value=0, max_value=23))
    minute = data.draw(st.integers(min_value=0, max_value=59))
    timestr = f"{hour:02d}:{minute:02d}"

    result = dateutil.parser.parse(timestr, default=default)

    assert result.year == default.year
    assert result.month == default.month
    assert result.day == default.day
    assert result.hour == hour
    assert result.minute == minute
    assert result.second == default.second
    assert result.microsecond == default.microsecond


@given(st.data())
def test_dateutil_parser_parse_dayfirst_and_yearfirst_control_ambiguous_dates(data):
    first = data.draw(st.integers(min_value=1, max_value=12))
    second = data.draw(st.integers(min_value=1, max_value=12))
    year = data.draw(st.integers(min_value=1900, max_value=2099))

    month_first_string = f"{first:02d}/{second:02d}/{year:04d}"

    month_first_result = dateutil.parser.parse(
        month_first_string,
        dayfirst=False,
        yearfirst=False,
    )
    day_first_result = dateutil.parser.parse(
        month_first_string,
        dayfirst=True,
        yearfirst=False,
    )

    assert month_first_result.year == year
    assert month_first_result.month == first
    assert month_first_result.day == second

    assert day_first_result.year == year
    assert day_first_result.month == second
    assert day_first_result.day == first

    year_first_string = f"{year:04d}/{first:02d}/{second:02d}"

    year_month_day_result = dateutil.parser.parse(
        year_first_string,
        yearfirst=True,
        dayfirst=False,
    )
    year_day_month_result = dateutil.parser.parse(
        year_first_string,
        yearfirst=True,
        dayfirst=True,
    )

    assert year_month_day_result.year == year
    assert year_month_day_result.month == first
    assert year_month_day_result.day == second

    assert year_day_month_result.year == year
    assert year_day_month_result.month == second
    assert year_day_month_result.day == first


# End program