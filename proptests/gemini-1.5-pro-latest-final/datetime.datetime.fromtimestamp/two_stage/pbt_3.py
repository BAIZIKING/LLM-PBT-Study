from hypothesis import given, strategies as st
import datetime

@given(st.data())
def test_datetime_datetime_fromtimestamp_range_limitation(data):
    # Generate timestamps outside the typical safe range
    unsafe_timestamps = st.integers(max_value=-2147483649) | st.integers(min_value=2147483648)
    timestamp = data.draw(unsafe_timestamps)
    with pytest.raises(OverflowError):
        datetime.datetime.fromtimestamp(timestamp)
# End program