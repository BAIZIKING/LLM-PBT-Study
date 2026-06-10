from hypothesis import given, strategies as st
from datetime import datetime
import time

# Generate a wide variety of timestamp inputs, including:
# - Timestamps within the valid range of 1970 to 2038 
# - Boundary values like the minimum and maximum valid timestamps
# - Invalid timestamps outside the supported range
# Also generate None and tzinfo objects to test the tz parameter
@given(st.one_of(
    st.floats(min_value=0, max_value=2**31-1), 
    st.just(0),
    st.just(2**31-1),
    st.floats(min_value=-2**31, max_value=-1), 
    st.floats(min_value=2**31, max_value=2**32),
    st.none(),
    st.builds(datetime.timezone, 
              st.timedeltas(min_value=-datetime.timedelta(hours=24), 
                            max_value=datetime.timedelta(hours=24)))))
def test_datetime_fromtimestamp(ts):
    if isinstance(ts, float) and 0 <= ts <= 2**31-1:
        # Valid timestamp, check that fromtimestamp is inverse of timestamp
        assert datetime.fromtimestamp(ts).timestamp() == ts
    elif ts is None or isinstance(ts, datetime.timezone):
        # Check that tz parameter accepts None and tzinfo objects
        assert isinstance(datetime.fromtimestamp(time.time(), tz=ts), datetime)
    else:
        # Check that out-of-range timestamps raise OverflowError
        try:
            datetime.fromtimestamp(ts)
            assert False, "Expected OverflowError"
        except OverflowError:
            pass
# End program        