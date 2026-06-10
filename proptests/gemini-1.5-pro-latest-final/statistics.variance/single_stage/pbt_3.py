from hypothesis import given, strategies as st
import statistics

# Summary: The generation strategy aims to create a diverse set of inputs for the statistics.variance function, 
# encompassing various data types, lengths, and potential edge cases.

@given(
    data=st.one_of(
        st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),  # Lists of floats (at least 2 elements)
        st.lists(st.decimals(allow_nan=False, allow_infinity=False), min_size=2),  # Lists of decimals (at least 2 elements)
        st.lists(st.fractions(), min_size=2),  # Lists of fractions (at least 2 elements)
        st.iterables(st.integers(), min_size=2),  # Iterables of integers (at least 2 elements)
    ),
    xbar=st.one_of(st.none(), st.floats(allow_nan=False, allow_infinity=False)),  # Optional mean (None or float)
)
def test_statistics_variance(data, xbar):
    # Properties to check:
    # 1. Calculation correctness: Verify that the calculated variance matches the expected result using a different implementation.
    # 2. Data type handling: Ensure consistent behavior for various numeric data types (floats, decimals, fractions, integers).
    # 3. Edge cases: Test behavior with empty lists, lists with NaNs or infinities (should raise StatisticsError).

    if xbar is None:
        expected_variance = statistics.pvariance(data)  # Calculate expected variance using population variance
    else:
        expected_variance = sum((x - xbar) ** 2 for x in data) / (len(data) - 1)  # Manually calculate expected variance

    try:
        result = statistics.variance(data, xbar)
        assert abs(result - expected_variance) < 1e-10  # Assert near equality due to potential floating-point precision issues
    except statistics.StatisticsError as e:
        assert len(data) < 2 or any(math.isnan(x) or math.isinf(x) for x in data)  # Check if error is raised for invalid input
# End program