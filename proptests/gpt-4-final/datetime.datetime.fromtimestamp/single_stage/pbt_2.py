from hypothesis import given, strategies as st
from datetime import datetime

@given(st.floats(min_value=-1e10, max_value=1e10, allow_nan=False, allow_infinity=False))
def test_datetime_fromtimestamp(timestamp):
    try:
        result = datetime.fromtimestamp(timestamp)
        assert result.year >= 1970 and result.year <= 2038
    except OverflowError:
        assert timestamp < 0 or timestamp > 3.1556926e9  # Timestamps for 1970 and 2038 in seconds