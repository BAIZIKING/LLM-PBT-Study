from hypothesis import given, strategies as st
import statistics

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_median_single_element(data):
    assert statistics.median([data]) == data
# End program 