from hypothesis import given, strategies as st
import statistics

# Summary: Generates lists of varying sizes containing positive floats.
@given(st.lists(st.floats(min_value=0.0001, allow_infinity=False, allow_nan=False), min_size=1))
def test_geometric_mean(data):
    # Check if the function raises StatisticsError for invalid inputs
    if any(x <= 0 for x in data):
        with pytest.raises(statistics.StatisticsError):
            statistics.geometric_mean(data)
    else:
        result = statistics.geometric_mean(data)
        # Check if the output is a float
        assert isinstance(result, float)
        # Check if geometric mean is less than or equal to arithmetic mean
        assert result <= statistics.mean(data)
# End program