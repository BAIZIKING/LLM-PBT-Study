from hypothesis import given, strategies as st
from datetime import datetime, date, timedelta
from dateutil.parser import parse, ParserError

# Summary: Generate documented parse scenarios: valid ISO datetime strings, date-only/time-only strings with defaults, timezone strings with ignoretz/tzinfos, ambiguous numeric dates with dayfirst, fuzzy strings with fuzzy_with_tokens, and invalid strings. Check parsed datetime fields, timezone behavior, fuzzy return shape/tokens, and ParserError for invalid input.
@given(st.data())
def test_dateutil_parser_parse(data):
    scenario = data.draw(
        st.sampled_from(
            [
                "iso_roundtrip",
                "default_date_only",
                "default_time_only",
                "ignoretz",
                "tzinfos_dict",
                "dayfirst_ambiguity",
                "fuzzy_with_tokens",
                "invalid_string",
            ]
        )
    )

    datetimes = st.datetimes(
        min_value=datetime(1000, 1, 1),
        max_value=datetime(9999, 12, 31, 23, 59, 59, 999999),
        timezones=st.none(),
    )

    if scenario == "iso_roundtrip":
        dt = data.draw(datetimes)
        sep = data.draw(st.sampled_from(["T", " "]))
        timestr = dt.isoformat(sep=sep, timespec="microseconds")

        result = parse(timestr)

        assert isinstance(result, datetime)
        assert (
            result.year,
            result.month,
            result.day,
            result.hour,
            result.minute,
            result.second,
            result.microsecond,
        ) == (
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
        )

    elif scenario == "default_date_only":
        d = data.draw(
            st.dates(
                min_value=date(1000, 1, 1),
                max_value=date(9999, 12, 31),
            )
        )
        default = data.draw(datetimes)
        timestr = f"{d.year:04d}-{d.month:02d}-{d.day:02d}"

        result = parse(timestr, default=default)

        assert (result.year, result.month, result.day) == (d.year, d.month, d.day)
        assert (
            result.hour,
            result.minute,
            result.second,
            result.microsecond,
        ) == (
            default.hour,
            default.minute,
            default.second,
            default.microsecond,
        )

    elif scenario == "default_time_only":
        default = data.draw(datetimes)
        hour = data.draw(st.integers(min_value=0, max_value=23))
        minute = data.draw(st.integers(min_value=0, max_value=59))
        second = data.draw(st.integers(min_value=0, max_value=59))
        microsecond = data.draw(st.integers(min_value=0, max_value=999999))
        timestr = f"{hour:02d}:{minute:02d}:{second:02d}.{microsecond:06d}"

        result = parse(timestr, default=default)

        assert (result.year, result.month, result.day) == (
            default.year,
            default.month,
            default.day,
        )
        assert (
            result.hour,
            result.minute,
            result.second,
            result.microsecond,
        ) == (
            hour,
            minute,
            second,
            microsecond,
        )

    elif scenario == "ignoretz":
        dt = data.draw(datetimes)
        sign = data.draw(st.sampled_from(["+", "-"]))
        offset_hour = data.draw(st.integers(min_value=0, max_value=23))
        offset_minute = data.draw(st.integers(min_value=0, max_value=59))
        timestr = (
            f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d} "
            f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}.{dt.microsecond:06d} "
            f"{sign}{offset_hour:02d}{offset_minute:02d}"
        )

        result = parse(timestr, ignoretz=True)

        assert result.tzinfo is None
        assert (
            result.year,
            result.month,
            result.day,
            result.hour,
            result.minute,
            result.second,
            result.microsecond,
        ) == (
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
        )

    elif scenario == "tzinfos_dict":
        dt = data.draw(datetimes)
        alias = data.draw(st.sampled_from(["BRST", "CST", "XST", "FOO"]))
        offset_sign = data.draw(st.sampled_from([-1, 1]))
        offset_hour = data.draw(st.integers(min_value=0, max_value=23))
        offset_minute = data.draw(st.integers(min_value=0, max_value=59))
        offset_seconds = offset_sign * ((offset_hour * 3600) + (offset_minute * 60))
        timestr = (
            f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d} "
            f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d} {alias}"
        )

        result = parse(timestr, tzinfos={alias: offset_seconds})

        assert result.tzinfo is not None
        assert result.utcoffset() == timedelta(seconds=offset_seconds)
        assert (
            result.year,
            result.month,
            result.day,
            result.hour,
            result.minute,
            result.second,
        ) == (
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
        )

    elif scenario == "dayfirst_ambiguity":
        first = data.draw(st.integers(min_value=1, max_value=12))
        second = data.draw(st.integers(min_value=1, max_value=12))
        year = data.draw(st.integers(min_value=0, max_value=99))
        timestr = f"{first:02d}/{second:02d}/{year:02d}"

        dmy = parse(timestr, dayfirst=True, yearfirst=False)
        mdy = parse(timestr, dayfirst=False, yearfirst=False)

        assert (dmy.day, dmy.month) == (first, second)
        assert (mdy.month, mdy.day) == (first, second)

    elif scenario == "fuzzy_with_tokens":
        d = data.draw(
            st.dates(
                min_value=date(1000, 1, 1),
                max_value=date(9999, 12, 31),
            )
        )
        hour = data.draw(st.integers(min_value=0, max_value=23))
        minute = data.draw(st.integers(min_value=0, max_value=59))
        second = data.draw(st.integers(min_value=0, max_value=59))
        prefix = data.draw(st.sampled_from(["note", "please ignore", "message says"]))
        suffix = data.draw(st.sampled_from(["done", "end text", "zzz"]))
        month_name = [
            "",
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
        ][d.month]
        core = (
            f"{month_name} {d.day}, {d.year:04d} "
            f"at {hour:02d}:{minute:02d}:{second:02d}"
        )
        timestr = f"{prefix} {core} {suffix}"

        result = parse(timestr, fuzzy_with_tokens=True)
        expected = datetime(d.year, d.month, d.day, hour, minute, second)

        assert isinstance(result, tuple)
        assert len(result) == 2
        parsed, ignored_tokens = result
        assert parsed == expected
        assert isinstance(ignored_tokens, tuple)
        assert "".join(ignored_tokens).strip() != ""

    else:
        bad = data.draw(
            st.lists(
                st.sampled_from(["nonsense", "blarg", "xxxx", "qwerty"]),
                min_size=1,
                max_size=5,
            ).map(" ".join)
        )

        try:
            parse(bad)
        except ParserError:
            pass
        else:
            assert False, "Invalid non-date strings should raise ParserError"

# End program