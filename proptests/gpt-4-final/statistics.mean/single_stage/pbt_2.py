from hypothesis import given, strategies as st
import statistics
from fractions import Fraction
from decimal import Decimal

# The test will generate lists of `int`, `float`, `Fraction`, and `Decimal` of varying lengths to cover all possible types mean() can handle.
# Empty sequences will also be generated to test the error handling.
@given(st.one_of(
    st.lists(st.integers()),
    st.lists(st.floats(allow_nan=False, allow_infinity=False)),
    st.lists(st.fractions()),
    st.lists(st.decimals(allow_nan=False, allow_infinity=False)),
    st.just([])
))
def test_statistics_mean(data):
    if not data:
        try:
            statistics.mean(data)
        except statistics.StatisticsError:
            assert True
    else:
        mean = statistics.mean(data)
        expected_mean = sum(data)/len(data)
        assert mean == expected_mean