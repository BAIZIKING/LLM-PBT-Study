from hypothesis import given, strategies as st
from datetime import datetime

@given(st.integers(min_value=0, max_value=2**31-1))
def test_datetime_fromtimestamp(timestamp):
    try:
        result = datetime.fromtimestamp(timestamp)
    except (OverflowError, OSError):
        pass  # As per the docs, these are expected for some input values. 
    else:
        assert isinstance(result, datetime)
        # The timestamp will be in the same timezone as the one used by the fromtimestamp.
        # Thus, converting the datetime object back into a timestamp should give a value very close to the original one.
        assert abs(result.timestamp() - timestamp) < 1
# End program