from hypothesis import given, strategies as st
import datetime

@given(st.floats(min_value=0, max_value=1e10))    # POSIX timestamp
def test_output_type(timestamp):
    result = datetime.datetime.fromtimestamp(timestamp)
    assert isinstance(result, datetime.datetime)

@given(st.floats(min_value=0, max_value=1e10))    # POSIX timestamp
def test_naive_when_tz_is_none(timestamp):
    result = datetime.datetime.fromtimestamp(timestamp)
    assert result.tzinfo is None

@given(st.floats(min_value=0, max_value=1e10))    # POSIX timestamp
def test_correct_local_conversion(timestamp):
    from_zone = datetime.timezone.utc
    to_zone = datetime.timezone(datetime.timedelta(hours=3))    # Arbitrary local timezone
    utc_time = datetime.datetime.utcfromtimestamp(timestamp)
    utc_time = utc_time.replace(tzinfo=from_zone)
    local_time = utc_time.astimezone(to_zone)    # Proper conversion to local time
    result = datetime.datetime.fromtimestamp(timestamp, tz=to_zone)
    # Only check down to the minutes to avoid discrepancy due to execution time
    assert result.hour == local_time.hour and result.minute == local_time.minute

@given(st.floats(min_value=0, max_value=1e10), st.integers(min_value=-11, max_value=14))    # POSIX timestamp and UTC offset
def test_correct_timezone_conversion(timestamp, offset):
    from_zone = datetime.timezone.utc
    to_zone = datetime.timezone(datetime.timedelta(hours=offset))    # Arbitrary timezone
    utc_time = datetime.datetime.utcfromtimestamp(timestamp)
    utc_time = utc_time.replace(tzinfo=from_zone)
    tz_time = utc_time.astimezone(to_zone)    # Proper conversion to timezone
    result = datetime.datetime.fromtimestamp(timestamp, tz=to_zone)
    # Only check down to the minutes to avoid discrepancy due to execution time
    assert result.hour == tz_time.hour and result.minute == tz_time.minute

# For the error handling test, we assume that the platform follows the common restriction of timestamps to years in 1970 through 2038
@given(st.floats(min_value=1e11, allow_infinity=True, allow_nan=False))
def test_error_handling(timestamp):
    try:
        datetime.datetime.fromtimestamp(timestamp)
    except OverflowError:
        pass
    except Exception as e:
        assert False, 'Raised wrong exception type: {}'.format(type(e).__name__)
    else:
        assert False, 'No exception raised for invalid timestamp'
# End program