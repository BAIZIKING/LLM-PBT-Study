from hypothesis import given, strategies as st
import datetime

# Generate a variety of valid and invalid timestamp values to test the full range 
# of behavior for datetime.fromtimestamp, including:
#  - Typical timestamps between 1970 and 2038 
#  - Boundary values like 0, very large/small timestamps
#  - Invalid timestamps outside the range supported by the platform
# Also generate some timezone values to test the optional tz parameter.
# Check the following properties based on the documentation:
#  - When tz is None, the returned datetime should be in local time and be naive
#  - When tz is provided, the datetime is converted to that timezone  
#  - OverflowError is raised for timestamps out of the supported range
#  - OSError is raised if localtime() or gmtime() fail
@given(st.one_of(
    st.floats(min_value=0, max_value=2**31-1), 
    st.floats(min_value=-2**31, max_value=0),
    st.floats(min_value=2**63, max_value=2**64-1),
    st.floats(min_value=-2**63, max_value=-2**62),
), st.one_of(st.none(), st.timezones()))
def test_datetime_fromtimestamp(ts, tz):
    try:
        dt = datetime.datetime.fromtimestamp(ts, tz)
        assert (tz is None and dt.tzinfo is None) or dt.tzinfo == tz
    except (OverflowError, OSError):
        assert (ts < 0 or ts > 2**31-1) 
# End program