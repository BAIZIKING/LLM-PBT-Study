from hypothesis import given, strategies as st, assume
import datetime
from dateutil.parser import isoparse
from dateutil import tz


# Property 1: Return type invariant
# For any valid ISO-8601 input string, the output is always a datetime.datetime.
@given(st.datetimes(
    min_value=datetime.datetime(1, 1, 1),
    max_value=datetime.datetime(9999, 12, 31),
))
def test_dateutil_parser_isoparse_return_type(dt):
    iso_str = dt.isoformat()
    result = isoparse(iso_str)
    assert isinstance(result, datetime.datetime)


# Property 2: Round-trip consistency
# Formatting a datetime as ISO and parsing it yields an equal datetime.
@given(st.datetimes(
    min_value=datetime.datetime(1, 1, 1),
    max_value=datetime.datetime(9999, 12, 31),
    timezones=st.one_of(
        st.none(),
        st.just(tz.tzutc()),
        st.builds(
            tz.tzoffset,
            st.none(),
            st.integers(min_value=-86340, max_value=86340),
        ),
    ),
))
def test_dateutil_parser_isoparse_roundtrip(dt):
    iso_str = dt.isoformat()
    result = isoparse(iso_str)
    assert result == dt


# Property 3: Default-to-lowest-value property
# Unspecified components default to their lowest valid value.
@given(
    year=st.integers(min_value=1, max_value=9999),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28),
)
def test_dateutil_parser_isoparse_defaults(year, month, day):
    # YYYY only -> month=1, day=1, time=0
    s_year = "{:04d}".format(year)
    r = isoparse(s_year)
    assert r.month == 1
    assert r.day == 1
    assert r.hour == 0
    assert r.minute == 0
    assert r.second == 0
    assert r.microsecond == 0
    assert r.tzinfo is None

    # YYYY-MM -> day=1, time=0
    s_ym = "{:04d}-{:02d}".format(year, month)
    r = isoparse(s_ym)
    assert r.day == 1
    assert r.hour == 0
    assert r.minute == 0
    assert r.second == 0
    assert r.microsecond == 0
    assert r.tzinfo is None

    # YYYY-MM-DDThh -> minute/second/microsecond default to 0
    s_ymd_h = "{:04d}-{:02d}-{:02d}T05".format(year, month, day)
    r = isoparse(s_ymd_h)
    assert r.hour == 5
    assert r.minute == 0
    assert r.second == 0
    assert r.microsecond == 0


# Property 4: UTC timezone normalization
# UTC-equivalent offsets yield tzutc; non-UTC offsets yield tzoffset matching.
@given(
    dt=st.datetimes(
        min_value=datetime.datetime(1, 1, 1),
        max_value=datetime.datetime(9999, 12, 31),
    ),
    offset_minutes=st.integers(min_value=-14 * 60, max_value=14 * 60),
)
def test_dateutil_parser_isoparse_tz_normalization(dt, offset_minutes):
    base = dt.strftime("%Y-%m-%dT%H:%M:%S")

    # UTC-equivalent forms
    for z in ("Z", "+00:00", "+0000", "+00"):
        r = isoparse(base + z)
        assert isinstance(r.tzinfo, tz.tzutc)
        assert r.utcoffset() == datetime.timedelta(0)

    # General offset
    sign = "+" if offset_minutes >= 0 else "-"
    abs_min = abs(offset_minutes)
    hh = abs_min // 60
    mm = abs_min % 60
    off_str = "{}{:02d}:{:02d}".format(sign, hh, mm)
    r = isoparse(base + off_str)
    expected = datetime.timedelta(minutes=offset_minutes)
    if offset_minutes == 0:
        assert isinstance(r.tzinfo, tz.tzutc)
    else:
        assert isinstance(r.tzinfo, tz.tzoffset)
    assert r.utcoffset() == expected


# Property 5: Naive vs. aware correspondence
# tzinfo is non-None iff the input contains a timezone offset.
@given(
    dt=st.datetimes(
        min_value=datetime.datetime(1, 1, 1),
        max_value=datetime.datetime(9999, 12, 31),
    ),
    has_tz=st.booleans(),
    offset_minutes=st.integers(min_value=-14 * 60, max_value=14 * 60),
)
def test_dateutil_parser_isoparse_naive_vs_aware(dt, has_tz, offset_minutes):
    base = dt.strftime("%Y-%m-%dT%H:%M:%S")
    if has_tz:
        sign = "+" if offset_minutes >= 0 else "-"
        abs_min = abs(offset_minutes)
        hh = abs_min // 60
        mm = abs_min % 60
        s = base + "{}{:02d}:{:02d}".format(sign, hh, mm)
        r = isoparse(s)
        assert r.tzinfo is not None
    else:
        r = isoparse(base)
        assert r.tzinfo is None
# End program