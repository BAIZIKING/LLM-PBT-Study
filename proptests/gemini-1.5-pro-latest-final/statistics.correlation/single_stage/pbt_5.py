from hypothesis import given, strategies as st
import statistics

# Summary: Generates diverse lists of numbers with varying lengths, data types, and value ranges.
@given(st.lists(st.one_of(st.integers(), st.floats()), min_size=1), 
       st.sampled_from(["linear", "ranked"]))
def test_statistics_correlation(data, method):
    x = data
    y = data[:]  # Create a copy to ensure equal lengths

    # Edge case: Test with empty lists
    if not x:
        with pytest.raises(statistics.StatisticsError):
            statistics.correlation(x, y, method=method)
        return

    # Test with lists of different lengths
    y.append(1)  # Make y longer than x
    with pytest.raises(statistics.StatisticsError):
        statistics.correlation(x, y, method=method)

    y.pop()  # Restore equal lengths

    # Calculate correlation and check output range
    r = statistics.correlation(x, y, method=method)
    assert -1 <= r <= 1

    # Method specific checks
    if method == "linear":
        # Compare with a known linear relationship
        assert statistics.correlation([1, 2, 3], [2, 4, 6]) > 0.99
    else:
        # Compare with a known monotonic relationship
        assert statistics.correlation([1, 2, 3], [3, 2, 1]) < -0.99
# End program