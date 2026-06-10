from hypothesis import given, strategies as st
from datetime import date, datetime, timedelta
from dateutil.parser import parse

# Summary: Generates several documented input shapes: fully specified ISO datetimes,
# ambiguous 3-integer dates controlled by dayfirst/yearfirst, time-only strings using
# a random default datetime, fuzzy natural-language strings using fuzzy/fuzzy_with_tokens,
# and timezone-bearing strings using tzinfos/ignoretz. The test checks that parsed
# datetime fields match the generated source values, default fills unspecified fields,
# ambiguity flags are honored, fuzzy_with_tokens returns the documented tuple shape,
# and ignoretz/tzinfos control whether tzinfo is present.
@given(st.data())
def test_dateutil_parser_parse(data):
    variant = data.draw(
        st.sampled_from(
            [
                "iso_datetime",
                "ambiguous_numeric_date",
                "time_only_with_default",
                "fuzzy_text",
                "timezone_alias",
            ]
        )
    )

    kwargs = {}
    expect_tuple = False
    expected_tz_offset_seconds = None

    if variant == "iso_datetime":
        dt = data.draw(
            st.datetimes(
                min_value=datetime(1, 1, 1, 0, 0, 0, 0),
                max_value=datetime(9999, 12, 31, 23, 59, 59, 999999),
                timezones=st.none(),
            )
        )
        sep = data.draw(st.sampled_from(["T", " "]))
        timestr = (
            f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}"
            f"{sep}{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
            f".{dt.microsecond:06d}"
        )
        kwargs["yearfirst"] = True
        kwargs["dayfirst"] = False
        expected = dt

    elif variant == "ambiguous_numeric_date":
        d = data.draw(
            st.dates(
                min_value=date(1900, 1, 1),
                max_value=date(2099, 12, 31),
            )
        )
        dayfirst = data.draw(st.booleans())
        yearfirst = data.draw(st.booleans())

        if yearfirst and dayfirst:
            timestr = f"{d.year:04d}/{d.day:02d}/{d.month:02d}"  # YDM
        elif yearfirst and not dayfirst:
            timestr = f"{d.year:04d}/{d.month:02d}/{d.day:02d}"  # YMD
        elif not yearfirst and dayfirst:
            timestr = f"{d.day:02d}/{d.month:02d}/{d.year:04d}"  # DMY
        else:
            timestr = f"{d.month:02d}/{d.day:02d}/{d.year:04d}"  # MDY

        kwargs["dayfirst"] = dayfirst
        kwargs["yearfirst"] = yearfirst
        expected = datetime(d.year, d.month, d.day)

    elif variant == "time_only_with_default":
        default = data.draw(
            st.datetimes(
                min_value=datetime(1, 1, 1, 0, 0, 0, 0),
                max_value=datetime(9999, 12, 31, 23, 59, 59, 999999),
                timezones=st.none(),
            )
        )
        hour = data.draw(st.integers(min_value=0, max_value=23))
        minute = data.draw(st.integers(min_value=0, max_value=59))
        second = data.draw(st.integers(min_value=0, max_value=59))
        include_microsecond = data.draw(st.booleans())

        if include_microsecond:
            microsecond = data.draw(st.integers(min_value=0, max_value=999999))
            timestr = f"{hour:02d}:{minute:02d}:{second:02d}.{microsecond:06d}"
        else:
            microsecond = default.microsecond
            timestr = f"{hour:02d}:{minute:02d}:{second:02d}"

        kwargs["default"] = default
        expected = default.replace(
            hour=hour,
            minute=minute,
            second=second,
            microsecond=microsecond,
        )

    elif variant == "fuzzy_text":
        month_names = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        d = data.draw(
            st.dates(
                min_value=date(1900, 1, 1),
                max_value=date(2099, 12, 31),
            )
        )
        hour_24 = data.draw(st.integers(min_value=0, max_value=23))
        minute = data.draw(st.integers(min_value=0, max_value=59))
        second = data.draw(st.integers(min_value=0, max_value=59))

        suffix = "AM" if hour_24 < 12 else "PM"
        hour_12 = hour_24 % 12 or 12

        timestr = (
            f"Today is {month_names[d.month - 1]} {d.day}, {d.year:04d} "
            f"at {hour_12}:{minute:02d}:{second:02d}{suffix}"
        )

        expect_tuple = data.draw(st.booleans())
        if expect_tuple:
            kwargs["fuzzy_with_tokens"] = True
        else:
            kwargs["fuzzy"] = True

        expected = datetime(d.year, d.month, d.day, hour_24, minute, second)

    else:
        d = data.draw(
            st.dates(
                min_value=date(1900, 1, 1),
                max_value=date(2099, 12, 31),
            )
        )
        hour = data.draw(st.integers(min_value=0, max_value=23))
        minute = data.draw(st.integers(min_value=0, max_value=59))
        second = data.draw(st.integers(min_value=0, max_value=59))
        tzname, offset_seconds = data.draw(
            st.sampled_from(
                [
                    ("BRST", -7200),
                    ("CST", -21600),
                ]
            )
        )
        ignoretz = data.draw(st.booleans())

        timestr = (
            f"{d.year:04d}-{d.month:02d}-{d.day:02d} "
            f"{hour:02d}:{minute:02d}:{second:02d} {tzname}"
        )
        kwargs["tzinfos"] = {"BRST": -7200, "CST": -21600}
        kwargs["ignoretz"] = ignoretz

        expected = datetime(d.year, d.month, d.day, hour, minute, second)
        expected_tz_offset_seconds = None if ignoretz else offset_seconds

    result = parse(timestr, **kwargs)

    if expect_tuple:
        assert isinstance(result, tuple)
        assert len(result) == 2
        parsed, ignored_tokens = result
        assert isinstance(parsed, datetime)
        assert isinstance(ignored_tokens, tuple)
        assert all(isinstance(token, str) for token in ignored_tokens)
        assert "Today is" in "".join(ignored_tokens)
        assert " at " in "".join(ignored_tokens)
    else:
        parsed = result
        assert isinstance(parsed, datetime)

    assert (
        parsed.year,
        parsed.month,
        parsed.day,
        parsed.hour,
        parsed.minute,
        parsed.second,
        parsed.microsecond,
    ) == (
        expected.year,
        expected.month,
        expected.day,
        expected.hour,
        expected.minute,
        expected.second,
        expected.microsecond,
    )

    if expected_tz_offset_seconds is None:
        assert parsed.tzinfo is None
    else:
        assert parsed.utcoffset() == timedelta(seconds=expected_tz_offset_seconds)

# End program