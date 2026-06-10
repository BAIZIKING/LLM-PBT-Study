from hypothesis import given, strategies as st
import datetime
import time

@given(st.floats(min_value=0, max_value=time.time()))
def test_fromtimestamp_components(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    assert dt.timestamp() == pytest.approx(timestamp)

@given(st.floats(min_value=0, max_value=time.time()))
def test_fromtimestamp_naive(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    assert dt.tzinfo is None

@given(st.floats(min_value=0, max_value=time.time()), st.timezones())
def test_fromtimestamp_aware(timestamp, tz):
    dt = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    assert dt.tzinfo == tz

@given(st.floats(max_value=-1e10) | st.floats(min_value=1e10))
def test_fromtimestamp_overflow(timestamp):
    with pytest.raises(OverflowError):
        datetime.datetime.fromtimestamp(timestamp)

@given(st.floats(min_value=0, max_value=time.time()))
def test_fromtimestamp_os_error(timestamp, monkeypatch):
    def mock_localtime(*args, **kwargs):
        raise OSError("Mocked localtime failure")
    
    monkeypatch.setattr(time, 'localtime', mock_localtime)
    with pytest.raises(OSError):
        datetime.datetime.fromtimestamp(timestamp)
# End program