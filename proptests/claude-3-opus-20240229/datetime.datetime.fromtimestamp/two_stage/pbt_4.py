from hypothesis import given, strategies as st
import datetime
import time

@given(st.integers(min_value=0, max_value=2**31-1))
def test_fromtimestamp_local_time(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    assert dt.timestamp() == timestamp

@given(st.integers(min_value=0, max_value=2**31-1), st.timezones())
def test_fromtimestamp_tzinfo(timestamp, tz):
    dt = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    assert dt.timestamp() == timestamp
    assert dt.tzinfo == tz

@given(st.integers(min_value=0, max_value=2**31-1))
def test_fromtimestamp_naive(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    assert dt.tzinfo is None

@given(st.integers(max_value=-1))
def test_fromtimestamp_overflow(timestamp):
    try:
        datetime.datetime.fromtimestamp(timestamp)
    except OverflowError:
        pass
    else:
        assert False, "Expected OverflowError"

@given(st.integers(min_value=2**63))
def test_fromtimestamp_os_error(timestamp):
    try:
        datetime.datetime.fromtimestamp(timestamp)
    except OSError:
        pass
    else:
        assert False, "Expected OSError"
# End program