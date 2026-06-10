from hypothesis import given, strategies as st
import datetime
import time

@given(st.floats(min_value=0, max_value=time.time()))
def test_fromtimestamp_local_time_correspondence(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    assert dt.timestamp() == timestamp

@given(st.floats(min_value=0, max_value=time.time()), st.timezones())
def test_fromtimestamp_tz_time_correspondence(timestamp, tz):
    dt = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    assert dt.timestamp() == timestamp

@given(st.floats(min_value=0, max_value=time.time()))
def test_fromtimestamp_naive_datetime(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    assert dt.tzinfo is None

@given(st.floats(max_value=-1e10) | st.floats(min_value=1e10))
def test_fromtimestamp_overflow_error(timestamp):
    try:
        datetime.datetime.fromtimestamp(timestamp)
        assert False
    except OverflowError:
        pass

@given(st.floats(min_value=0, max_value=time.time()))
def test_fromtimestamp_os_error(timestamp, monkeypatch):
    def mock_localtime(timestamp):
        raise OSError("Mock OSError")
    monkeypatch.setattr(time, 'localtime', mock_localtime)
    try:
        datetime.datetime.fromtimestamp(timestamp)
        assert False
    except OSError:
        pass
# End program