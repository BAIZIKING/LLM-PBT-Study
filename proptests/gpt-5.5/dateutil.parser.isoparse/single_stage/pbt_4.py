from hypothesis import given, strategies as st
from datetime import date, datetime, time, timedelta
from io import StringIO

from dateutil import parser, tz


# Summary: Generate documented valid ISO-8601 inputs across common dates, ISO week dates,
# optional complete time portions, midnight/24:00, fractional seconds with dot or comma,
# optional timezone offsets in all supported forms, and either plain strings or streams.
# Invalid strings are deliberately avoided because the documentation says parser strictness
# for invalid inputs is not stable. The test checks that parsed datetimes have the expected
# defaulted components, week-date conversion, 24:00 rollover, fractional-second value, and
# timezone offset/UTC handling.
@given(st.data())
def test_dateutil_parser_isoparse(data):
    date_kind = data.draw(
        st.sampled_from(
            [
                "year",
                "year_month_ext",
                "year_month_basic",
                "date_ext",
                "date_basic",
                "week_ext",
                "week_basic",
                "week_day_ext",
                "week_day_basic",
            ]
        )
    )

    if date_kind == "year":
        year = data.draw(st.integers(min_value=1, max_value=9999))
        iso_string = f"{year:04d}"
        base_date = date(year, 1, 1)
        complete_date = False

    elif date_kind in {"year_month_ext", "year_month_basic"}:
        year = data.draw(st.integers(min_value=1, max_value=9999))
        month = data.draw(st.integers(min_value=1, max_value=12))
        iso_string = (
            f"{year:04d}-{month:02d}"
            if date_kind == "year_month_ext"
            else f"{year:04d}{month:02d}"
        )
        base_date = date(year, month, 1)
        complete_date = False

    elif date_kind in {"date_ext", "date_basic"}:
        base_date = data.draw(st.dates(min_value=date.min, max_value=date.max))
        iso_string = (
            base_date.strftime("%Y-%m-%d")
            if date_kind == "date_ext"
            else base_date.strftime("%Y%m%d")
        )
        complete_date = True

    else:
        generated_date = data.draw(st.dates(min_value=date.min, max_value=date.max))
        iso_year, iso_week, iso_weekday = generated_date.isocalendar()

        if date_kind in {"week_ext", "week_basic"}:
            iso_string = (
                f"{iso_year:04d}-W{iso_week:02d}"
                if date_kind == "week_ext"
                else f"{iso_year:04d}W{iso_week:02d}"
            )
            base_date = date.fromisocalendar(iso_year, iso_week, 1)
            complete_date = False
        else:
            iso_string = (
                f"{iso_year:04d}-W{iso_week:02d}-{iso_weekday}"
                if date_kind == "week_day_ext"
                else f"{iso_year:04d}W{iso_week:02d}{iso_weekday}"
            )
            base_date = generated_date
            complete_date = True

    expected_date = base_date
    expected_hour = 0
    expected_minute = 0
    expected_second = 0
    expected_microsecond = 0
    expected_offset = None

    if complete_date and data.draw(st.booleans()):
        separator = data.draw(st.sampled_from(["T", " "]))
        time_kind = data.draw(
            st.sampled_from(
                [
                    "hour",
                    "hour_minute_ext",
                    "hour_minute_basic",
                    "hour_minute_second_ext",
                    "hour_minute_second_basic",
                    "fraction_ext",
                ]
            )
        )

        use_24_hour = (
            base_date < date.max
            and data.draw(st.booleans())
            and time_kind != "fraction_ext"
        )

        if use_24_hour:
            hour = 24
            minute = 0
            second = 0
            microsecond = 0
        else:
            hour = data.draw(st.integers(min_value=0, max_value=23))
            minute = data.draw(st.integers(min_value=0, max_value=59))
            second = data.draw(st.integers(min_value=0, max_value=59))
            microsecond = 0

        if time_kind == "hour":
            time_string = f"{hour:02d}"
            expected_hour, expected_minute, expected_second, expected_microsecond = (
                hour,
                0,
                0,
                0,
            )

        elif time_kind == "hour_minute_ext":
            time_string = f"{hour:02d}:{minute:02d}"
            expected_hour, expected_minute, expected_second, expected_microsecond = (
                hour,
                minute,
                0,
                0,
            )

        elif time_kind == "hour_minute_basic":
            time_string = f"{hour:02d}{minute:02d}"
            expected_hour, expected_minute, expected_second, expected_microsecond = (
                hour,
                minute,
                0,
                0,
            )

        elif time_kind == "hour_minute_second_ext":
            time_string = f"{hour:02d}:{minute:02d}:{second:02d}"
            expected_hour, expected_minute, expected_second, expected_microsecond = (
                hour,
                minute,
                second,
                0,
            )

        elif time_kind == "hour_minute_second_basic":
            time_string = f"{hour:02d}{minute:02d}{second:02d}"
            expected_hour, expected_minute, expected_second, expected_microsecond = (
                hour,
                minute,
                second,
                0,
            )

        else:
            fraction_digits = data.draw(
                st.text(
                    alphabet=st.characters(min_codepoint=ord("0"), max_codepoint=ord("9")),
                    min_size=1,
                    max_size=6,
                )
            )
            decimal_separator = data.draw(st.sampled_from([".", ","]))
            time_string = (
                f"{hour:02d}:{minute:02d}:{second:02d}"
                f"{decimal_separator}{fraction_digits}"
            )
            expected_hour = hour
            expected_minute = minute
            expected_second = second
            expected_microsecond = int(fraction_digits.ljust(6, "0"))

        if expected_hour == 24:
            expected_date = base_date + timedelta(days=1)
            expected_hour = 0

        if data.draw(st.booleans()):
            tz_kind = data.draw(st.sampled_from(["Z", "HH", "HHMM", "HH:MM"]))
            if tz_kind == "Z":
                tz_string = "Z"
                expected_offset = timedelta(0)
            else:
                sign = data.draw(st.sampled_from(["+", "-"]))
                offset_hour = data.draw(st.integers(min_value=0, max_value=23))
                offset_minute = (
                    0
                    if tz_kind == "HH"
                    else data.draw(st.integers(min_value=0, max_value=59))
                )

                if tz_kind == "HH":
                    tz_string = f"{sign}{offset_hour:02d}"
                elif tz_kind == "HHMM":
                    tz_string = f"{sign}{offset_hour:02d}{offset_minute:02d}"
                else:
                    tz_string = f"{sign}{offset_hour:02d}:{offset_minute:02d}"

                offset = timedelta(hours=offset_hour, minutes=offset_minute)
                expected_offset = offset if sign == "+" else -offset

            time_string += tz_string

        iso_string = f"{iso_string}{separator}{time_string}"

    expected = datetime.combine(
        expected_date,
        time(
            expected_hour,
            expected_minute,
            expected_second,
            expected_microsecond,
        ),
    )

    dt_input = data.draw(st.sampled_from([iso_string, StringIO(iso_string)]))
    parsed = parser.isoparse(dt_input)

    assert isinstance(parsed, datetime)
    assert parsed.replace(tzinfo=None) == expected

    if expected_offset is None:
        assert parsed.tzinfo is None
    else:
        assert parsed.utcoffset() == expected_offset
        if expected_offset == timedelta(0):
            assert parsed.tzinfo == tz.tzutc()


# End program