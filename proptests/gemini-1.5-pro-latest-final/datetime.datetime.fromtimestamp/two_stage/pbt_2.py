from hypothesis import given, strategies as st
import datetime

# Define a strategy for generating timestamps within a safe range
safe_timestamps = st.integers(min_value=datetime.datetime(1970, 1, 1).timestamp(),
                              max_value=datetime.datetime(2038, 1, 19).timestamp())

# Define a strategy for generating optional timezones
timezones = st.one_of(st.none(), st.builds(datetime.timezone.utc))

@given(safe_timestamps, timezones)
def test_datetime_datetime_fromtimestamp_type(timestamp, tz):
    dt_obj = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    assert isinstance(dt_obj, datetime.datetime)

@given(safe_timestamps, timezones)
def test_datetime_datetime_fromtimestamp_year_range(timestamp, tz):
    dt_obj = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    assert 1970 <= dt_obj.year <= 2038

@given(safe_timestamps)
def test_datetime_datetime_fromtimestamp_naive_timezone(timestamp):
    dt_obj = datetime.datetime.fromtimestamp(timestamp)  # No tz specified
    assert dt_obj.tzinfo is None

@given(safe_timestamps, timezones)
def test_datetime_datetime_fromtimestamp_timezone(timestamp, tz):
    dt_obj = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    if tz is None:
        assert dt_obj.tzinfo is None
    else:
        assert dt_obj.tzinfo == tz

@given(st.tuples(safe_timestamps, safe_timestamps), timezones)
def test_datetime_datetime_fromtimestamp_monotonicity(timestamps, tz):
    timestamp_a, timestamp_b = timestamps
    dt_obj_a = datetime.datetime.fromtimestamp(timestamp_a, tz=tz)
    dt_obj_b = datetime.datetime.fromtimestamp(timestamp_b, tz=tz)
    if timestamp_a > timestamp_b:
        assert dt_obj_a >= dt_obj_b

@given(safe_timestamps, timezones)
def test_datetime_datetime_fromtimestamp_consistency(timestamp, tz):
    dt_obj_1 = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    dt_obj_2 = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    assert dt_obj_1 == dt_obj_2
# End program