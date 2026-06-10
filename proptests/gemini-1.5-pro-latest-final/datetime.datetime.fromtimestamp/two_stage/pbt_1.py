from hypothesis import given, strategies as st
import datetime

# Define a strategy for generating timestamps within a reasonable range
safe_timestamps = st.integers(min_value=-2**31, max_value=2**31-1)

# Define a strategy for generating optional timezones
optional_timezones = st.one_of(st.none(), st.timezones())

@given(timestamp=safe_timestamps, tz=optional_timezones)
def test_datetime_fromtimestamp_type_consistency(timestamp, tz):
    result = datetime.datetime.fromtimestamp(timestamp, tz)
    assert isinstance(result, datetime.datetime)

@given(timestamp=safe_timestamps)
def test_datetime_fromtimestamp_timestamp_relationship(timestamp):
    result = datetime.datetime.fromtimestamp(timestamp)
    epoch_time = datetime.datetime.fromtimestamp(0)
    if timestamp >= 0:
        assert result >= epoch_time
    else:
        assert result < epoch_time

@given(timestamp=safe_timestamps, tz=optional_timezones)
def test_datetime_fromtimestamp_timezone_dependence(timestamp, tz):
    result_naive = datetime.datetime.fromtimestamp(timestamp)
    result_aware = datetime.datetime.fromtimestamp(timestamp, tz)
    if tz is None:
        assert result_naive == result_aware
    else:
        assert result_aware.tzinfo == tz

@given(timestamp1=safe_timestamps, timestamp2=safe_timestamps, tz=optional_timezones)
def test_datetime_fromtimestamp_uniqueness(timestamp1, timestamp2, tz):
    if timestamp1 != timestamp2:
        dt1 = datetime.datetime.fromtimestamp(timestamp1, tz)
        dt2 = datetime.datetime.fromtimestamp(timestamp2, tz)
        assert dt1 != dt2

@given(st.integers(max_value=-2**31 - 1))
def test_datetime_fromtimestamp_overflow_below(timestamp):
    with pytest.raises(OverflowError):
        datetime.datetime.fromtimestamp(timestamp)

@given(st.integers(min_value=2**31))
def test_datetime_fromtimestamp_overflow_above(timestamp):
    with pytest.raises(OverflowError):
        datetime.datetime.fromtimestamp(timestamp)
# End program