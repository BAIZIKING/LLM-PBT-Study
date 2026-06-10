from hypothesis import given, strategies as st, assume
import datetime
import dateutil
from dateutil.parser import isoparse
from dateutil import tz


# Property 1: Output type is datetime.datetime for valid ISO-8601 strings
@given(st.datetimes())
def test_dateutil_parser_isoparse_output_type(dt):
    iso_str = dt.isoformat()
    result = isoparse(iso_str)
    assert isinstance(result, datetime.datetime)
# End program


# Property 2: Round-trip consistency for naive datetimes
@given(st.datetimes(
    min_value=datetime.datetime(1, 1, 1, 0, 0, 0),
    max_value=datetime.datetime(9999, 12, 31, 23, 59, 59),
))
def test_dateutil_parser_isoparse_roundtrip_naive(dt):
    iso_str = dt.isoformat()
    result = isoparse(iso_str)
    assert result == dt
# End program


# Property 2b: Round-trip consistency for aware datetimes with fixed offsets
@given(
    st.datetimes(
        min_value=datetime.datetime(1, 1, 1, 0, 0, 0),
        max_value=datetime.datetime(9999, 12, 31, 23, 59, 59),
    ),
    st.integers(min_value=-23 * 3600, max_value=23 * 3600),
)
def test_dateutil_parser_isoparse_roundtrip_aware(dt, offset_seconds):
    tzobj = tz.tzoffset(None, offset_seconds)
    aware = dt.replace(tzinfo=tzobj)
    iso_str = aware.isoformat()
    result = isoparse(iso_str)
    # Both represent the same instant in time
    assert result.utcoffset() == aware.utcoffset()
    assert result.replace(tzinfo=None) == aware.replace(tzinfo=None)
# End program


# Property 3: Unspecified components default to their lowest value
@given(
    st.integers(min_value=1, max_value=9999),
    st.integers(min_value=1, max_value=12),
)
def test_dateutil_parser_isoparse_defaults(year, month):
    iso_str = "{:04d}-{:02d}".format(year, month)
    result = isoparse(iso_str)
    assert result.year == year
    assert result.month == month
    assert result.day == 1
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
    assert result.microsecond == 0
# End program


# Property 4: UTC-equivalent offsets yield tzutc, non-UTC yield tzoffset, naive yields None
@given(
    st.datetimes(
        min_value=datetime.datetime(1, 1, 1, 0, 0, 0),
        max_value=datetime.datetime(9999, 12, 31, 23, 59, 59),
    ),
    st.integers(min_value=-23 * 3600, max_value=23 * 3600),
)
def test_dateutil_parser_isoparse_timezone_representation(dt, offset_seconds):
    # Naive case
    naive_result = isoparse(dt.isoformat())
    assert naive_result.tzinfo is None

    # UTC case using 'Z'
    utc_str = dt.isoformat() + "Z"
    utc_result = isoparse(utc_str)
    assert isinstance(utc_result.tzinfo, tz.tzutc)

    # Offset case
    tzobj = tz.tzoffset(None, offset_seconds)
    aware_str = dt.replace(tzinfo=tzobj).isoformat()
    offset_result = isoparse(aware_str)
    if offset_seconds == 0:
        assert isinstance(offset_result.tzinfo, tz.tzutc)
    else:
        assert isinstance(offset_result.tzinfo, tz.tzoffset)
        assert offset_result.utcoffset() == datetime.timedelta(seconds=offset_seconds)
# End program


# Property 5: Component values fall within valid ranges and offset matches input
@given(
    st.datetimes(
        min_value=datetime.datetime(1, 1, 1, 0, 0, 0),
        max_value=datetime.datetime(9999, 12, 31, 23, 59, 59),
    ),
    st.integers(min_value=-23 * 3600, max_value=23 * 3600),
)
def test_dateutil_parser_isoparse_component_bounds(dt, offset_seconds):
    tzobj = tz.tzoffset(None, offset_seconds)
    aware = dt.replace(tzinfo=tzobj)
    result = isoparse(aware.isoformat())

    assert 1 <= result.month <= 12
    assert 1 <= result.day <= 31
    assert 0 <= result.hour <= 23
    assert 0 <= result.minute <= 59
    assert 0 <= result.second <= 59
    assert 0 <= result.microsecond <= 999999
    # Offset encoded in input matches output
    assert result.utcoffset() == datetime.timedelta(seconds=offset_seconds)
# End program