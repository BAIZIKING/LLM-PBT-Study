from hypothesis import given, strategies as st
import datetime
import pytest

@given(st.integers(min_value=0, max_value=2**31-1))
def test_fromtimestamp_corresponds_to_input(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    assert dt.timestamp() == pytest.approx(timestamp)

@given(st.integers(min_value=0, max_value=2**31-1))
def test_fromtimestamp_returns_naive_datetime(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    assert dt.tzinfo is None

@given(st.integers(min_value=0, max_value=2**31-1), st.timezones())
def test_fromtimestamp_with_tz_returns_aware_datetime(timestamp, tz):
    dt = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    assert dt.tzinfo is tz

@given(st.integers(max_value=-1))
def test_fromtimestamp_raises_overflow_error_for_negative_timestamp(timestamp):
    with pytest.raises(OverflowError):
        datetime.datetime.fromtimestamp(timestamp)

@given(st.integers(min_value=2**63))
def test_fromtimestamp_raises_overflow_error_for_large_timestamp(timestamp):
    with pytest.raises(OverflowError):
        datetime.datetime.fromtimestamp(timestamp)
# End program