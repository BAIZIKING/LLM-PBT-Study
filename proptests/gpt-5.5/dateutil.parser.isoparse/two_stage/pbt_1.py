from hypothesis import given, strategies as st
import dateutil
import dateutil.parser
import dateutil.tz
import datetime


def _draw_date(data):
    return data.draw(
        st.dates(
            min_value=datetime.date(1, 1, 1),
            max_value=datetime.date(9999, 12, 31),
        )
    )


def _format_complete_date(data, d):
    fmt = data.draw(st.sampled_from(["extended", "basic"]))
    if fmt == "extended":
        return f"{d.year:04d}-{d.month:02d}-{d.day:02d}"
    return f"{d.year:04d}{d.month:02d}{d.day:02d}"


def _draw_time(data):
    hour = data.draw(st.integers(min_value=0, max_value=23))
    minute = data.draw(st.integers(min_value=0, max_value=59))
    second = data.draw(st.integers(min_value=0, max_value=59))
    microsecond_digits = data.draw(st.text("0123456789", min_size=1, max_size=6))
    decimal_separator = data.draw(st.sampled_from([".", ","]))

    fmt = data.draw(
        st.sampled_from(
            [
                "hh",
                "hh:mm",
                "hhmm",
                "hh:mm:ss",
                "hhmmss",
                "hh:mm:ss.frac",
            ]
        )
    )

    if fmt == "hh":
        return f"{hour:02d}"
    if fmt == "hh:mm":
        return f"{hour:02d}:{minute:02d}"
    if fmt == "hhmm":
        return f"{hour:02d}{minute:02d}"
    if fmt == "hh:mm:ss":
        return f"{hour:02d}:{minute:02d}:{second:02d}"
    if fmt == "hhmmss":
        return f"{hour:02d}{minute:02d}{second:02d}"
    return f"{hour:02d}:{minute:02d}:{second:02d}{decimal_separator}{microsecond_digits}"


def _draw_timezone(data):
    tz_kind = data.draw(st.sampled_from(["none", "Z", "hh", "hhmm", "hh:mm"]))
    if tz_kind == "none":
        return ""
    if tz_kind == "Z":
        return "Z"

    sign = data.draw(st.sampled_from(["+", "-"]))
    hour = data.draw(st.integers(min_value=0, max_value=23))
    minute = data.draw(st.integers(min_value=0, max_value=59))

    if tz_kind == "hh":
        return f"{sign}{hour:02d}"
    if tz_kind == "hhmm":
        return f"{sign}{hour:02d}{minute:02d}"
    return f"{sign}{hour:02d}:{minute:02d}"


@given(st.data())
def test_dateutil_parser_isoparse_property_returns_datetime(data):
    d = _draw_date(data)

    shape = data.draw(st.sampled_from(["date_only", "datetime"]))

    if shape == "date_only":
        date_fmt = data.draw(
            st.sampled_from(["year", "year_month_extended", "year_month_basic", "full"])
        )
        if date_fmt == "year":
            dt_str = f"{d.year:04d}"
        elif date_fmt == "year_month_extended":
            dt_str = f"{d.year:04d}-{d.month:02d}"
        elif date_fmt == "year_month_basic":
            dt_str = f"{d.year:04d}{d.month:02d}"
        else:
            dt_str = _format_complete_date(data, d)
    else:
        dt_str = _format_complete_date(data, d) + "T" + _draw_time(data) + _draw_timezone(data)

    parsed = dateutil.parser.isoparse(dt_str)

    assert isinstance(parsed, datetime.datetime)


@given(st.data())
def test_dateutil_parser_isoparse_property_unspecified_components_default_lowest(data):
    d = _draw_date(data)
    date_fmt = data.draw(
        st.sampled_from(
            [
                "year",
                "year_month_extended",
                "year_month_basic",
                "full_extended",
                "full_basic",
            ]
        )
    )

    if date_fmt == "year":
        dt_str = f"{d.year:04d}"
        expected_month = 1
        expected_day = 1
    elif date_fmt == "year_month_extended":
        dt_str = f"{d.year:04d}-{d.month:02d}"
        expected_month = d.month
        expected_day = 1
    elif date_fmt == "year_month_basic":
        dt_str = f"{d.year:04d}{d.month:02d}"
        expected_month = d.month
        expected_day = 1
    elif date_fmt == "full_extended":
        dt_str = f"{d.year:04d}-{d.month:02d}-{d.day:02d}"
        expected_month = d.month
        expected_day = d.day
    else:
        dt_str = f"{d.year:04d}{d.month:02d}{d.day:02d}"
        expected_month = d.month
        expected_day = d.day

    parsed = dateutil.parser.isoparse(dt_str)

    assert parsed.year == d.year
    assert parsed.month == expected_month
    assert parsed.day == expected_day
    assert parsed.hour == 0
    assert parsed.minute == 0
    assert parsed.second == 0
    assert parsed.microsecond == 0


@given(st.data())
def test_dateutil_parser_isoparse_property_fractional_seconds_become_microseconds(data):
    d = _draw_date(data)
    hour = data.draw(st.integers(min_value=0, max_value=23))
    minute = data.draw(st.integers(min_value=0, max_value=59))
    second = data.draw(st.integers(min_value=0, max_value=59))
    fraction = data.draw(st.text("0123456789", min_size=1, max_size=6))
    separator = data.draw(st.sampled_from([".", ","]))

    dt_str = (
        f"{d.year:04d}-{d.month:02d}-{d.day:02d}"
        f"T{hour:02d}:{minute:02d}:{second:02d}{separator}{fraction}"
    )

    parsed = dateutil.parser.isoparse(dt_str)
    expected_microsecond = int(fraction.ljust(6, "0"))

    assert parsed.microsecond == expected_microsecond


@given(st.data())
def test_dateutil_parser_isoparse_property_utc_offsets_produce_utc_tzinfo(data):
    d = _draw_date(data)
    hour = data.draw(st.integers(min_value=0, max_value=23))
    minute = data.draw(st.integers(min_value=0, max_value=59))
    second = data.draw(st.integers(min_value=0, max_value=59))
    utc_offset = data.draw(st.sampled_from(["Z", "+00", "+0000", "+00:00"]))

    dt_str = (
        f"{d.year:04d}-{d.month:02d}-{d.day:02d}"
        f"T{hour:02d}:{minute:02d}:{second:02d}{utc_offset}"
    )

    parsed = dateutil.parser.isoparse(dt_str)

    assert isinstance(parsed.tzinfo, dateutil.tz.tzutc)
    assert parsed.utcoffset() == datetime.timedelta(0)


@given(st.data())
def test_dateutil_parser_isoparse_property_24_hour_midnight_advances_to_next_day(data):
    d = data.draw(
        st.dates(
            min_value=datetime.date(1, 1, 1),
            max_value=datetime.date(9999, 12, 30),
        )
    )
    midnight_format = data.draw(st.sampled_from(["24:00", "2400", "24:00:00", "240000"]))

    dt_str = f"{d.year:04d}-{d.month:02d}-{d.day:02d}T{midnight_format}"

    parsed = dateutil.parser.isoparse(dt_str)
    expected_date = d + datetime.timedelta(days=1)

    assert parsed == datetime.datetime(
        expected_date.year,
        expected_date.month,
        expected_date.day,
        0,
        0,
        0,
        0,
    )


# End program