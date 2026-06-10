from hypothesis import given, strategies as st
import datetime

# Generate a wide variety of timestamp values to test fromtimestamp
# Includes integers, floats, positives, negatives, and special values 
# like very large/small numbers to test overflow behavior.
# Also generate None and tzinfo objects to test the tz parameter.
@given(st.one_of(
    st.none(), 
    st.builds(datetime.timezone), 
    st.integers(min_value=-2**63, max_value=2**63-1),
    st.floats(allow_nan=False, allow_infinity=False),
    st.just(datetime.datetime.min.timestamp()),
    st.just(datetime.datetime.max.timestamp())
))
def test_datetime_fromtimestamp(timestamp):
    if isinstance(timestamp, (int, float)):
        dt = datetime.datetime.fromtimestamp(timestamp)
        assert isinstance(dt, datetime.datetime)
        assert dt.timestamp() == timestamp
    else:
        try:
            dt = datetime.datetime.fromtimestamp(0, tz=timestamp) 
            assert dt.tzinfo == timestamp
        except TypeError:
            assert timestamp is None
# End program        