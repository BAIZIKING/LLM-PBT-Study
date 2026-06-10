from hypothesis import given, strategies as st
from datetime import datetime, timezone 
import time

# Generate a wide variety of timestamps to test, including:
# - Timestamps within the typical supported range of 1970-2038 
# - Timestamps outside the typical supported range
# - Negative timestamps (before the epoch)
# - Timestamps with fractional seconds 
# - Very large and very small timestamps
# Also generate some timezone objects to test the tz parameter.
@given(st.one_of(
    st.floats(min_value=0, max_value=2**31-1), 
    st.floats(min_value=-2**31, max_value=0), 
    st.floats(min_value=2**31, max_value=2**63-1),
    st.floats(min_value=-2**63, max_value=-2**31)
),
st.timezones() | st.none())
def test_datetime_fromtimestamp(ts, tz):
    try:
        dt = datetime.fromtimestamp(ts, tz)
    except (ValueError, OSError, OverflowError):
        # OSError, ValueError (pre Python3.3) or OverflowError expected if timestamp is out of range
        assert ts < 0 or ts > 2**31-1
    else:
        assert dt.timestamp() == ts  # resulting datetime should match original timestamp
        if tz is None:
            assert dt.tzinfo is None  # dt should be naive if no tz given
        else:
            assert dt.tzinfo == tz and dt == datetime.fromtimestamp(ts, tz) # dt should have tz
# End program        