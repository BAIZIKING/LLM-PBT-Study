from hypothesis import given, strategies as st
import dateutil
import dateutil.parser
from datetime import datetime


@given(st.data())
def test_dateutil_parser_parse_returns_datetime_when_not_fuzzy_with_tokens(data):
    dt = data.draw(
        st.datetimes(
            min_value=datetime(1900, 1, 1, 0, 0, 0),
            max_value=datetime(2099, 12, 31, 23, 59, 59),
            timezones=st.none(),
        )
    )
    timestr = (
        f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d} "
        f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
    )

    parsed = dateutil.parser.parse(timestr, fuzzy_with_tokens=False)

    assert isinstance(parsed, datetime)


@given(st.data())
def test_dateutil_parser_parse_fuzzy_with_tokens_returns_datetime_and_tokens(data):
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]

    dt = data.draw(
        st.datetimes(
            min_value=datetime(1900, 1, 1, 0, 0, 0),
            max_value=datetime(2099, 12, 31, 23, 59, 59),
            timezones=st.none(),
        )
    )
    hour12 = data.draw(st.integers(min_value=1, max_value=12))
    am_pm = data.draw(st.sampled_from(["AM", "PM"]))

    timestr = (
        f"Today is {month_names[dt.month - 1]} {dt.day}, {dt.year} "
        f"at {hour12}:{dt.minute:02d}:{dt.second:02d}{am_pm}"
    )

    parsed = dateutil.parser.parse(timestr, fuzzy_with_tokens=True)

    assert isinstance(parsed, tuple)
    assert len(parsed) == 2
    assert isinstance(parsed[0], datetime)
    assert isinstance(parsed[1], tuple)
    assert all(isinstance(token, str) for token in parsed[1])


@given(st.data())
def test_dateutil_parser_parse_ignoretz_returns_naive_datetime(data):
    dt = data.draw(
        st.datetimes(
            min_value=datetime(1900, 1, 1, 0, 0, 0),
            max_value=datetime(2099, 12, 31, 23, 59, 59),
            timezones=st.none(),
        )
    )
    offset_minutes = data.draw(st.integers(min_value=-12 * 60, max_value=14 * 60))
    sign = "+" if offset_minutes >= 0 else "-"
    absolute_offset = abs(offset_minutes)
    offset_hours, offset_remainder_minutes = divmod(absolute_offset, 60)

    timestr = (
        f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d} "
        f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d} "
        f"{sign}{offset_hours:02d}:{offset_remainder_minutes:02d}"
    )

    parsed = dateutil.parser.parse(timestr, ignoretz=True)

    assert isinstance(parsed, datetime)
    assert parsed.tzinfo is None


@given(st.data())
def test_dateutil_parser_parse_uses_default_for_omitted_date_fields(data):
    default = data.draw(
        st.datetimes(
            min_value=datetime(1900, 1, 1, 0, 0, 0),
            max_value=datetime(2099, 12, 31, 23, 59, 59),
            timezones=st.none(),
        )
    )
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


@given(st.data())
def test_dateutil_parser_parse_dayfirst_and_yearfirst_control_ambiguous_dates(data):
    dayfirst_day = data.draw(st.integers(min_value=1, max_value=12))
    dayfirst_month = data.draw(st.integers(min_value=1, max_value=12))
    dayfirst_year = data.draw(st.integers(min_value=0, max_value=99))

    dayfirst_timestr = f"{dayfirst_day:02d}/{dayfirst_month:02d}/{dayfirst_year:02d}"
    dayfirst_parsed = dateutil.parser.parse(
        dayfirst_timestr,
        dayfirst=True,
        yearfirst=False,
    )

    assert dayfirst_parsed.day == dayfirst_day
    assert dayfirst_parsed.month == dayfirst_month

    yearfirst_year = data.draw(st.integers(min_value=0, max_value=99))
    yearfirst_month = data.draw(st.integers(min_value=1, max_value=12))
    yearfirst_day = data.draw(st.integers(min_value=1, max_value=28))

    yearfirst_timestr = f"{yearfirst_year:02d}/{yearfirst_month:02d}/{yearfirst_day:02d}"
    yearfirst_parsed = dateutil.parser.parse(
        yearfirst_timestr,
        dayfirst=False,
        yearfirst=True,
    )

    assert yearfirst_parsed.month == yearfirst_month
    assert yearfirst_parsed.day == yearfirst_day


# End program