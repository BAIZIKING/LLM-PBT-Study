from hypothesis import given, strategies as st
import datetime
from dateutil.parser import isoparse
from dateutil import tz

# Summary: Generate valid datetimes (with optional UTC/fixed-offset tzinfo), serialize
# them into a randomly chosen ISO-8601 format variant (basic/extended date, T/space
# separator, varying time precision, dot/comma decimal sep, and various tz-offset
# encodings), tracking which components are specified. Then check that isoparse round-trips
# correctly with unspecified components defaulting to their lowest value, returns a
# datetime, and normalizes UTC-equivalent offsets to tzutc.
@given(st.data())
def test_dateutil_parser_isoparse(data):
    # Choose a timezone: none, UTC, or a fixed offset (whole minutes)
    tz_choice = data.draw(st.sampled_from(["none", "utc", "offset"]))
    if tz_choice == "none":
        tzinfo = None
    elif tz_choice == "utc":
        tzinfo = datetime.timezone.utc
    else:
        # offset in whole minutes within +/- 23:59
        total_minutes = data.draw(st.integers(min_value=-(23 * 60 + 59),
                                              max_value=(23 * 60 + 59)))
        tzinfo = datetime.timezone(datetime.timedelta(minutes=total_minutes))

    dt = data.draw(st.datetimes(
        min_value=datetime.datetime(1, 1, 1),
        max_value=datetime.datetime(9999, 12, 31, 23, 59, 59, 999999),
        timezones=st.just(tzinfo) if tzinfo is not None else st.none(),
    ))

    # ---- Build the date portion ----
    extended = data.draw(st.booleans())  # use dashes/colons or not
    if extended:
        date_str = f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}"
    else:
        date_str = f"{dt.year:04d}{dt.month:02d}{dt.day:02d}"

    # ---- Build the time portion ----
    # precision: 0 = none (date only), else include time with given precision
    precision = data.draw(st.sampled_from(["none", "h", "m", "s", "us"]))

    expected_hour = expected_min = expected_sec = expected_us = 0

    if precision == "none":
        time_str = ""
        offset_str = ""  # no time => no offset
        sep = ""
    else:
        sep = data.draw(st.sampled_from(["T", " "]))
        expected_hour = dt.hour
        if extended:
            colon = ":"
        else:
            colon = ""

        if precision == "h":
            time_str = f"{dt.hour:02d}"
        elif precision == "m":
            time_str = f"{dt.hour:02d}{colon}{dt.minute:02d}"
            expected_min = dt.minute
        elif precision == "s":
            time_str = f"{dt.hour:02d}{colon}{dt.minute:02d}{colon}{dt.second:02d}"
            expected_min = dt.minute
            expected_sec = dt.second
        else:  # us
            decimal_sep = data.draw(st.sampled_from([".", ","]))
            time_str = (f"{dt.hour:02d}{colon}{dt.minute:02d}{colon}{dt.second:02d}"
                        f"{decimal_sep}{dt.microsecond:06d}")
            expected_min = dt.minute
            expected_sec = dt.second
            expected_us = dt.microsecond

        # ---- Build the timezone offset portion ----
        if tzinfo is None:
            offset_str = ""
        elif tz_choice == "utc":
            offset_str = data.draw(st.sampled_from(["Z", "+00:00", "+0000", "+00"]))
        else:
            off = dt.utcoffset()
            total = int(off.total_seconds())
            sign = "+" if total >= 0 else "-"
            total = abs(total)
            oh = total // 3600
            om = (total % 3600) // 60
            offset_form = data.draw(st.sampled_from(["colon", "compact", "hour_only"]))
            if offset_form == "hour_only" and om != 0:
                offset_form = "colon"  # can't represent minutes with hour-only
            if offset_form == "colon":
                offset_str = f"{sign}{oh:02d}:{om:02d}"
            elif offset_form == "compact":
                offset_str = f"{sign}{oh:02d}{om:02d}"
            else:  # hour_only
                offset_str = f"{sign}{oh:02d}"

    iso_str = f"{date_str}{sep}{time_str}{offset_str}"

    result = isoparse(iso_str)

    # Property 2: return type is datetime.datetime
    assert isinstance(result, datetime.datetime)

    # Property 1: round-trip correctness with defaulting of unspecified components
    assert result.year == dt.year
    assert result.month == dt.month
    assert result.day == dt.day
    assert result.hour == expected_hour
    assert result.minute == expected_min
    assert result.second == expected_sec
    assert result.microsecond == expected_us

    # Property 3: timezone correctness / UTC normalization
    if precision == "none" or tzinfo is None:
        assert result.tzinfo is None
    else:
        # compare actual offsets rather than tzinfo identity
        assert result.utcoffset() == dt.utcoffset()
        if tz_choice == "utc" or result.utcoffset() == datetime.timedelta(0):
            # UTC-equivalent offsets normalized to tzutc
            assert result.tzinfo == tz.tzutc()
# End program