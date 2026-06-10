from hypothesis import given, strategies as st
import statistics

# Summary: Generates lists of positive floats with varying lengths, including edge cases.
@given(st.lists(st.floats(min_value=1e-6, max_value=1e6), min_size=1))
def test_geometric_mean(data):
    # Check for emptiness and positivity
    assert data and all(x > 0 for x in data)
    
    # Calculate geometric mean manually
    manual_mean = (statistics.prod(data)) ** (1/len(data))
    
    # Compare with statistics.geometric_mean
    computed_mean = statistics.geometric_mean(data)
    assert computed_mean == manual_mean
    
    # Test error handling (empty list, zero, negative value)
    assert_raises(StatisticsError, statistics.geometric_mean, [])
    assert_raises(StatisticsError, statistics.geometric_mean, [1, 0, 2])
    assert_raises(StatisticsError, statistics.geometric_mean, [1, -2, 3])
# End program