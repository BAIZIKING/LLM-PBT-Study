from hypothesis import given, strategies as st

from datetime import datetime, timedelta
from dateutil.parser import ParserError, parse, parserinfo
from dateutil.tz import tzoffset


# Summary: Generate parserinfo/default objects, parse flags, custom tzinfos, invalid noise,
# and valid date strings in full datetime, date-only, time-only, named-month, timezone-alias,
# and fuzzy-wrapper forms. Check documented success shapes, default-field replacement,
# ignoretz/tzinfos behavior, fuzzy_with_tokens tuple behavior, and documented failures.
@given(st.data())
def test_dateutil_parser_parse(data):
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]

    base = data.draw(
        st.datetimes(
            min_value=datetime(1, 1, 1),
            max_value=datetime(9999, 12, 31, 23, 59, 59, 999999),
            timezones=st.none(),
        )
    )
    default = data.draw(
        st.datetimes(
            min_value=datetime(1, 1, 1),
            max_value=datetime(9999, 12, 31, 23, 59, 59, 999999),
            timezones=st.none(),
        )
    )

    parser_info = data.draw(
        st.one_of(
            st.none(),
            st.builds(
                parserinfo,
                dayfirst=st.booleans(),
                yearfirst=st.booleans(),
            ),
        )
    )

    ignoretz = data.draw(st.booleans())
    dayfirst = data.draw(st.one_of(st.none(), st.booleans()))
    yearfirst = data.draw(st.one_of(st.none(), st.booleans()))
    fuzzy_with_tokens = data.draw(st.booleans())

    case = data.draw(
        st.sampled_from(
            [
                "full_numeric",
                "date_only",
                "time_only",
                "month_name",
                "tz_alias",
                "fuzzy",
                "invalid",
            ]
        )
    )

    time_part = (
        f"{base.hour:02d}:{base.minute:02d}:"
        f"{base.second:02d}.{base.microsecond:06d}"
    )
    full_numeric = (
        f"{base.year:04d}-{base.month:02d}-{base.day:02d} {time_part}"
    )

    tzinfos = None
    expected_offset = None

    if case == "full_numeric":
        timestr = full_numeric
        fuzzy = data.draw(st.booleans())
        expected = base

    elif case == "date_only":
        timestr = f"{base.year:04d}-{base.month:02d}-{base.day:02d}"
        fuzzy = data.draw(st.booleans())
        expected = datetime(
            base.year,
            base.month,
            base.day,
            default.hour,
            default.minute,
            default.second,
            default.microsecond,
        )

    elif case == "time_only":
        timestr = time_part
        fuzzy = data.draw(st.booleans())
        expected = datetime(
            default.year,
            default.month,
            default.day,
            base.hour,
            base.minute,
            base.second,
            base.microsecond,
        )

    elif case == "month_name":
        timestr = (
            f"{months[base.month - 1]} {base.day}, "
            f"{base.year:04d} {time_part}"
        )
        fuzzy = data.draw(st.booleans())
        expected = base

    elif case == "tz_alias":
        tzname, tzvalue, expected_offset = data.draw(
            st.sampled_from(
                [
                    ("BRST", -7200, -7200),
                    ("CST", tzoffset("CST", -21600), -21600),
                    ("XST", 19800, 19800),
                ]
            )
        )
        timestr = f"{full_numeric} {tzname}"
        fuzzy = data.draw(st.booleans())

        if data.draw(st.booleans()):
            tzinfos = {tzname: tzvalue}
        else:
            def tzinfos(name, offset):
                return {tzname: tzvalue}.get(name)

        expected = base

    elif case == "fuzzy":
        timestr = f"Today is {full_numeric} at trailing text"
        fuzzy = True
        expected = base

    else:
        timestr = data.draw(
            st.text(
                alphabet=st.sampled_from(list("qQ!?;# \t")),
                min_size=1,
                max_size=40,
            )
        )
        fuzzy = data.draw(st.booleans())
        expected = None

    kwargs = {
        "default": default,
        "ignoretz": ignoretz,
        "dayfirst": dayfirst,
        "yearfirst": yearfirst,
        "fuzzy": fuzzy,
        "fuzzy_with_tokens": fuzzy_with_tokens,
    }
    if tzinfos is not None:
        kwargs["tzinfos"] = tzinfos

    try:
        parsed = parse(timestr, parserinfo=parser_info, **kwargs)
    except (ParserError, OverflowError):
        assert case == "invalid"
        return

    assert case != "invalid"

    if fuzzy_with_tokens:
        assert isinstance(parsed, tuple)
        assert len(parsed) == 2
        result, tokens = parsed
        assert isinstance(tokens, tuple)
        assert all(isinstance(token, str) for token in tokens)

        if case == "fuzzy":
            joined_tokens = "".join(tokens)
            assert "Today" in joined_tokens
            assert "trailing" in joined_tokens
    else:
        result = parsed

    assert isinstance(result, datetime)

    if case == "tz_alias":
        assert result.replace(tzinfo=None) == expected
        if ignoretz:
            assert result.tzinfo is None
        else:
            assert result.tzinfo is not None
            assert result.utcoffset() == timedelta(seconds=expected_offset)
    else:
        assert result == expected
        assert result.tzinfo is None

    if ignoretz:
        assert result.tzinfo is None
# End program