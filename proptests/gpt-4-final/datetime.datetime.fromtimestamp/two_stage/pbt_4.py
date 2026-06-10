from hypothesis import given, strategies as st
import datetime

@given(st.integers(min_value=-2**31, max_value=2**31-1), st.one_of(st.none(), st.datetimes()))
def test_fromtimestamp_output_type(timestamp, tz):
    # 1. The output of `fromtimestamp()` is a datetime object
    assert isinstance(datetime.datetime.fromtimestamp(timestamp, tz), datetime.datetime)

@given(st.integers(min_value=-2**31, max_value=2**31-1))
def test_fromtimestamp_input_not_altered(timestamp):
    # 2. The timestamp input is not altered
    original_timestamp = timestamp
    datetime.datetime.fromtimestamp(timestamp)
    assert original_timestamp == timestamp

@given(st.one_of(st.none(), st.datetimes()), st.datetimes())
def test_fromtimestamp_timezones(tz, timestamp):
    # 3. Timezone Transformation
    # 4. Conversion to local timezone for None tz
    timestamp = int(timestamp.timestamp())
    result = datetime.datetime.fromtimestamp(timestamp, tz)
    if tz is None:
        assert result.tzinfo is None
    else:
        assert result.tzinfo == tz.tzinfo

@given(st.integers(min_value=-2**31, max_value=2**31-1))
def test_fromtimestamp_exceptions(timestamp):
    # 5. Exception Handling
    try:
        datetime.datetime.fromtimestamp(timestamp)
    except OverflowError:
        assert timestamp < -2**31 or timestamp > 2**31 - 1
    except OSError:
        assert False  # Should not cause OSError for valid inputs
    else:
        assert True  # No exception
# End program