from hypothesis import given, strategies as st
import dateutil
import dateutil.parser
import dateutil.tz
import datetime


_MIN_DATE = datetime.date(1, 1, 1)
_MAX_DATE = datetime.date(9999, 12, 31)


def _date_string(d, compact=False):
    if compact:
        return f"{d.year:04d}{d.month:02d}{d.day:02d}"
    return f"{d.year:04d}-{d.month:02d}-{d.day:02d}"


def _draw_offset(data, allow_none=True):
    choices = ["z", "colon", "compact", "hour"]
    if allow_none:
        choices.append("none")

    kind = data.draw(st.sampled_from(choices))

    if kind == "none":
        return "", None

    if kind == "z":
        return "Z", datetime.timedelta(0)

    sign = data.draw(st.sampled_from(["+", "-"]))
    sign_multiplier = 1 if sign == "+" else -1

    hour = data.draw(st.integers(min_value=0, max_value=23))

    if kind == "hour":
        minute = 0
        text = f"{sign}{hour:02d}"
    else:
        minute = data.draw(st.integers(min_value=0, max_value=59))
        if kind == "colon":
            text = f"{sign}{hour:02d}:{minute:02d}"
        else:
            text = f"{sign}{hour:02d}{minute:02d}"

    offset = sign_multiplier * datetime.timedelta(hours=hour, minutes=minute)
    return text, offset


@given(st.data())
def test_dateutil_parser_isoparse_represents_encoded_datetime(data):
    d = data.draw(st.dates(min_value=_MIN_DATE, max_value=_MAX_DATE))
    compact_date = data.draw(st.booleans())
    date_text = _date_string(d, compact=compact_date)

    include_time = data.draw(st.booleans())

    hour = minute = second = microsecond = 0
    offset_text = ""
    expected_offset = None

    if include_time:
        time_kind = data.draw(st.sampled_from(["hour", "minute", "second", "fraction"]))
        hour = data.draw(st.integers(min_value=0, max_value=23))

        if time_kind in {"minute", "second", "fraction"}:
            minute = data.draw(st.integers(min_value=0, max_value=59))

        if time_kind in {"second", "fraction"}:
            second = data.draw(st.integers(min_value=0, max_value=59))

        if time_kind == "hour":
            time_text = f"{hour:02d}"
        elif time_kind == "minute":
            time_text = f"{hour:02d}:{minute:02d}"
        elif time_kind == "second":
            time_text = f"{hour:02d}:{minute:02d}:{second:02d}"
        else:
            fraction = data.draw(st.text(alphabet="0123456789", min_size=1, max_size=6))
            microsecond = int(fraction.ljust(6, "0"))
            time_text = f"{hour:02d}:{minute:02d}:{second:02d}.{fraction}"

        offset_text, expected_offset = _draw_offset(data, allow_none=True)
        text = f"{date_text}T{time_text}{offset_text}"
    else:
        text = date_text

    parsed = dateutil.parser.isoparse(text)

    assert parsed.year == d.year
    assert parsed.month == d.month
    assert parsed.day == d.day
    assert parsed.hour == hour
    assert parsed.minute == minute
    assert parsed.second == second
    assert parsed.microsecond == microsecond
    assert parsed.utcoffset() == expected_offset


@given(st.data())
def test_dateutil_parser_isoparse_omitted_components_default_to_lowest_values(data):
    mode = data.draw(
        st.sampled_from(
            [
                "year",
                "year_month_extended",
                "year_month_compact",
                "date_extended",
                "date_compact",
            ]
        )
    )

    if mode == "year":
        year = data.draw(st.integers(min_value=1, max_value=9999))
        text = f"{year:04d}"
        expected_month = 1
        expected_day = 1
    elif mode in {"year_month_extended", "year_month_compact"}:
        year = data.draw(st.integers(min_value=1, max_value=9999))
        month = data.draw(st.integers(min_value=1, max_value=12))
        text = f"{year:04d}-{month:02d}" if mode == "year_month_extended" else f"{year:04d}{month:02d}"
        expected_month = month
        expected_day = 1
    else:
        d = data.draw(st.dates(min_value=_MIN_DATE, max_value=_MAX_DATE))
        text = _date_string(d, compact=(mode == "date_compact"))
        year = d.year
        expected_month = d.month
        expected_day = d.day

    parsed = dateutil.parser.isoparse(text)

    assert parsed.year == year
    assert parsed.month == expected_month
    assert parsed.day == expected_day
    assert parsed.hour == 0
    assert parsed.minute == 0
    assert parsed.second == 0
    assert parsed.microsecond == 0


@given(st.data())
def test_dateutil_parser_isoparse_extended_and_compact_representations_are_equal(data):
    d = data.draw(st.dates(min_value=_MIN_DATE, max_value=_MAX_DATE))
    mode = data.draw(st.sampled_from(["date", "hour", "minute", "second"]))

    extended = _date_string(d, compact=False)
    compact = _date_string(d, compact=True)

    if mode != "date":
        hour = data.draw(st.integers(min_value=0, max_value=23))

        if mode == "hour":
            extended_time = compact_time = f"{hour:02d}"
        elif mode == "minute":
            minute = data.draw(st.integers(min_value=0, max_value=59))
            extended_time = f"{hour:02d}:{minute:02d}"
            compact_time = f"{hour:02d}{minute:02d}"
        else:
            minute = data.draw(st.integers(min_value=0, max_value=59))
            second = data.draw(st.integers(min_value=0, max_value=59))
            extended_time = f"{hour:02d}:{minute:02d}:{second:02d}"
            compact_time = f"{hour:02d}{minute:02d}{second:02d}"

        extended = f"{extended}T{extended_time}"
        compact = f"{compact}T{compact_time}"

    assert dateutil.parser.isoparse(extended) == dateutil.parser.isoparse(compact)


@given(st.data())
def test_dateutil_parser_isoparse_timezone_offsets_match_encoded_offsets(data):
    d = data.draw(st.dates(min_value=_MIN_DATE, max_value=_MAX_DATE))
    hour = data.draw(st.integers(min_value=0, max_value=23))
    minute = data.draw(st.integers(min_value=0, max_value=59))
    second = data.draw(st.integers(min_value=0, max_value=59))
    offset_text, expected_offset = _draw_offset(data, allow_none=False)

    text = (
        f"{_date_string(d)}"
        f"T{hour:02d}:{minute:02d}:{second:02d}"
        f"{offset_text}"
    )

    parsed = dateutil.parser.isoparse(text)

    assert parsed.utcoffset() == expected_offset

    if expected_offset == datetime.timedelta(0):
        assert isinstance(parsed.tzinfo, dateutil.tz.tzutc)
    else:
        assert isinstance(parsed.tzinfo, dateutil.tz.tzoffset)


@given(st.data())
def test_dateutil_parser_isoparse_fractional_seconds_dot_and_comma_are_equivalent(data):
    d = data.draw(st.dates(min_value=_MIN_DATE, max_value=_MAX_DATE))
    hour = data.draw(st.integers(min_value=0, max_value=23))
    minute = data.draw(st.integers(min_value=0, max_value=59))
    second = data.draw(st.integers(min_value=0, max_value=59))
    fraction = data.draw(st.text(alphabet="0123456789", min_size=1, max_size=6))

    prefix = (
        f"{_date_string(d)}"
        f"T{hour:02d}:{minute:02d}:{second:02d}"
    )

    parsed_dot = dateutil.parser.isoparse(f"{prefix}.{fraction}")
    parsed_comma = dateutil.parser.isoparse(f"{prefix},{fraction}")

    expected_microsecond = int(fraction.ljust(6, "0"))

    assert parsed_dot == parsed_comma
    assert parsed_dot.microsecond == expected_microsecond
    assert parsed_comma.microsecond == expected_microsecond


# End program