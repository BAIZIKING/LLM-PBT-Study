from hypothesis import given, strategies as st
import datetime

# Summary: Generate a wide range of timestamp values including boundary cases.
# Check that fromtimestamp() returns a datetime matching the input timestamp.
# Also check proper error raising for out-of-range or invalid timestamps.
@given(st.one_of(
    st.floats(min_value=-10**8, max_value=10**8), 
    st.just(datetime.datetime.min.timestamp()),
    st.just(datetime.datetime.max.timestamp())
))
def test_datetime_fromtimestamp(ts):
    try:
        dt = datetime.datetime.fromtimestamp(ts)
        assert dt.timestamp() == ts
    except (OverflowError, OSError):
        # Verify OverflowError is raised for unsupported timestamp values
        # and OSError for localtime()/gmtime() failures
        assert (ts < datetime.datetime.min.timestamp() or 
                ts > datetime.datetime.max.timestamp())
# End program        