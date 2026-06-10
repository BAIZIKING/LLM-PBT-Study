from hypothesis import given, strategies as st
import datetime

_SAFE_TIMESTAMPS = st.integers(min_value=0, max_value=2_000_000_000)
_TIMEZONES = st.builds(
    lambda minutes: datetime.timezone(datetime.timedelta(minutes=minutes)),
    st.integers(min_value=-23 * 60 - 59, max_value=23 * 60 + 59),
)

@given(st.data())
def test_datetime_datetime_fromtimestamp_returns_datetime_instance(data):
    timestamp = data.draw(_SAFE_TIMESTAMPS)
    use_tz = data.draw(st.booleans())

    if use_tz:
        tz = data.draw(_TIMEZONES)
        result = datetime.datetime.fromtimestamp(timestamp, tz)
    else:
        result = datetime.datetime.fromtimestamp(timestamp)

    assert isinstance(result, datetime.datetime)

@given(st.data())
def test_datetime_datetime_fromtimestamp_without_tz_returns_naive_datetime(data):
    timestamp = data.draw(_SAFE_TIMESTAMPS)

    result = datetime.datetime.fromtimestamp(timestamp)

    assert result.tzinfo is None

@given(st.data())
def test_datetime_datetime_fromtimestamp_with_tz_returns_aware_datetime(data):
    timestamp = data.draw(_SAFE_TIMESTAMPS)
    tz = data.draw(_TIMEZONES)

    result = datetime.datetime.fromtimestamp(timestamp, tz)

    assert result.tzinfo is not None
    assert result.utcoffset() is not None

@given(st.data())
def test_datetime_datetime_fromtimestamp_with_tz_preserves_timestamp(data):
    timestamp = data.draw(_SAFE_TIMESTAMPS)
    tz = data.draw(_TIMEZONES)

    result = datetime.datetime.fromtimestamp(timestamp, tz)

    assert result.timestamp() == float(timestamp)

@given(st.data())
def test_datetime_datetime_fromtimestamp_fold_is_valid(data):
    timestamp = data.draw(_SAFE_TIMESTAMPS)
    use_tz = data.draw(st.booleans())

    if use_tz:
        tz = data.draw(_TIMEZONES)
        result = datetime.datetime.fromtimestamp(timestamp, tz)
    else:
        result = datetime.datetime.fromtimestamp(timestamp)

    assert result.fold in (0, 1)

# End program