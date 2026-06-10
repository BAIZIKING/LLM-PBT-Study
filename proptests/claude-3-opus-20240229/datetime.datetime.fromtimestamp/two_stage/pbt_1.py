from hypothesis import given, strategies as st
import datetime
import time

@given(st.floats(min_value=0, max_value=time.time()))
def test_fromtimestamp_local_time_correspondence(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    assert dt.timestamp() == timestamp

@given(st.floats(min_value=0, max_value=time.time()), st.timezones())
def test_fromtimestamp_timezone_correspondence(timestamp, tz):
    dt = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    assert dt.timestamp() == timestamp
    assert dt.tzinfo == tz

@given(st.floats(min_value=0, max_value=time.time()))
def test_fromtimestamp_naive_datetime(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    assert dt.tzinfo is None

@given(st.floats(max_value=-1e10) | st.floats(min_value=1e10))
def test_fromtimestamp_overflow_error(timestamp):
    try:
        datetime.datetime.fromtimestamp(timestamp)
        assert False, "Expected OverflowError"
    except OverflowError:
        pass

@given(st.floats(min_value=0, max_value=time.time()))
def test_fromtimestamp_os_error(timestamp, monkeypatch):
    def mock_localtime(seconds):
        raise OSError("Mock OSError")
    
    monkeypatch.setattr(time, 'localtime', mock_localtime)
    
    try:
        datetime.datetime.fromtimestamp(timestamp)
        assert False, "Expected OSError"
    except OSError:
        pass
# End program