from hypothesis import given, strategies as st
import datetime
from dateutil import parser as dateutil_parser

# Summary: Generate random datetimes, serialize them into randomly-chosen valid
# ISO-8601 formats (basic/extended, varying completeness, optional fractional
# seconds with '.'/',', optional timezone offset), then check that isoparse
# round-trips the specified components, defaults unspecified components to their
# lowest value, returns a datetime, and handles timezone offsets correctly.
@given(st.data())
def test_dateutil_parser_isoparse(data):
    dt = data.draw(st.datetimes(
        min_value=datetime.datetime(1, 1, 1),
        max_value=datetime.datetime(9999, 12, 31, 23, 59, 59, 999999),
    ))

    extended = data.draw(st.booleans())           # use separators (:, -) or not
    sep = data.draw(st.sampled_from(["T", " "]))   # date/time separator
    # completeness level: how many time components to include
    level = data.draw(st.sampled_from(["date", "hh", "hhmm", "hhmmss", "hhmmssf"]))
    tz_kind = data.draw(st.sampled_from(["none", "Z", "offset_colon",
                                         "offset_nocolon", "offset_hh"]))
    offset_hours = data.draw(st.integers(min_value=-23, max_value=23))
    offset_minutes = data.draw(st.sampled_from([0, 15, 30, 45]))
    decimal_comma = data.draw(st.booleans())

    # --- Build the date portion ---
    if extended:
        date_str = "{:04d}-{:02d}-{:02d}".format(dt.year, dt.month, dt.day)
    else:
        date_str = "{:04d}{:02d}{:02d}".format(dt.year, dt.month, dt.day)

    # Expected components default to lowest values
    exp_hour = exp_min = exp_sec = exp_micro = 0

    # --- Build the time portion ---
    time_str = ""
    if level != "date":
        exp_hour = dt.hour
        hh = "{:02d}".format(dt.hour)
        time_str = hh
        if level in ("hhmm", "hhmmss", "hhmmssf"):
            exp_min = dt.minute
            mm = "{:02d}".format(dt.minute)
            time_str += (":" + mm) if extended else mm
        if level in ("hhmmss", "hhmmssf"):
            exp_sec = dt.second
            ss = "{:02d}".format(dt.second)
            time_str += (":" + ss) if extended else ss
        if level == "hhmmssf":
            exp_micro = dt.microsecond
            frac = "{:06d}".format(dt.microsecond)
            dot = "," if decimal_comma else "."
            time_str += dot + frac

    # --- Build the timezone portion ---
    expected_offset = None  # None means naive
    tz_str = ""
    if level != "date":  # offsets only meaningful alongside a time
        if tz_kind == "Z":
            tz_str = "Z"
            expected_offset = datetime.timedelta(0)
        elif tz_kind == "offset_colon":
            sign = "+" if offset_hours >= 0 else "-"
            tz_str = "{}{:02d}:{:02d}".format(sign, abs(offset_hours), offset_minutes)
            sgn = 1 if offset_hours >= 0 else -1
            expected_offset = sgn * datetime.timedelta(
                hours=abs(offset_hours), minutes=offset_minutes)
        elif tz_kind == "offset_nocolon":
            sign = "+" if offset_hours >= 0 else "-"
            tz_str = "{}{:02d}{:02d}".format(sign, abs(offset_hours), offset_minutes)
            sgn = 1 if offset_hours >= 0 else -1
            expected_offset = sgn * datetime.timedelta(
                hours=abs(offset_hours), minutes=offset_minutes)
        elif tz_kind == "offset_hh":
            sign = "+" if offset_hours >= 0 else "-"
            tz_str = "{}{:02d}".format(sign, abs(offset_hours))
            sgn = 1 if offset_hours >= 0 else -1
            expected_offset = sgn * datetime.timedelta(hours=abs(offset_hours))

    # --- Assemble the full ISO-8601 string ---
    if time_str:
        iso_str = date_str + sep + time_str + tz_str
    else:
        iso_str = date_str

    result = dateutil_parser.isoparse(iso_str)

    # Property 1: result is always a datetime
    assert isinstance(result, datetime.datetime), (
        "isoparse did not return a datetime for {!r}".format(iso_str))

    # Property 2: specified components match; unspecified default to lowest value
    assert result.year == dt.year, iso_str
    assert result.month == dt.month, iso_str
    assert result.day == dt.day, iso_str
    assert result.hour == exp_hour, iso_str
    assert result.minute == exp_min, iso_str
    assert result.second == exp_sec, iso_str
    assert result.microsecond == exp_micro, iso_str

    # Property 3: timezone offset semantics
    if expected_offset is None:
        assert result.tzinfo is None or result.utcoffset() is None, (
            "Expected naive datetime for {!r}".format(iso_str))
    else:
        assert result.utcoffset() == expected_offset, (
            "Offset mismatch for {!r}: got {}, expected {}".format(
                iso_str, result.utcoffset(), expected_offset))
# End program