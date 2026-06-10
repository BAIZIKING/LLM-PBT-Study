from hypothesis import given, strategies as st
import statistics

# Summary: Generates lists of floats, including edge cases (empty, zeros, negatives)
@given(st.one_of(
    st.none(),  # Empty list
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1),  # Lists with at least one float
    st.floats(allow_nan=False, allow_infinity=False),  # Single float
))
def test_statistics_geometric_mean(data):
    if data is None or any(x <= 0 for x in data):
        with pytest.raises(statistics.StatisticsError):
            statistics.geometric_mean(data)
    else:
        # Calculate geometric mean manually for comparison
        product = 1
        for x in data:
            product *= x
        expected_mean = product ** (1/len(data))
        assert math.isclose(statistics.geometric_mean(data), expected_mean)
# End program