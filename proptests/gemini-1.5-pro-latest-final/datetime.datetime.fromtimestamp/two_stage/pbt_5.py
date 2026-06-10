from hypothesis import given, strategies as st
import datetime

@given(timestamp=st.integers(min_value=-2147483648, max_value=2147483647), tz=st.none() | st.timezones())
def test_datetime_datetime_fromtimestamp_leap_second_difference(timestamp, tz):
    try:
        dt = datetime.datetime.fromtimestamp(timestamp, tz=tz)
        difference = abs(timestamp - dt.timestamp())
        assert difference <= 27  # Number of leap seconds since 1970
    except OverflowError:
        pass
# End program 