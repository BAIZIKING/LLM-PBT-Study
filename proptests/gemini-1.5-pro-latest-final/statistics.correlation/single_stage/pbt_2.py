from hypothesis import given, strategies as st
import statistics

# Summary: Generates lists of varying lengths, data types, and value ranges to test different correlation scenarios and edge cases.
@given(st.data())
def test_statistics_correlation(data):
    # Generate lists with varying lengths and data types
    x = data.draw(st.lists(st.one_of(st.floats(), st.integers(), st.text()), min_size=2))
    y = data.draw(st.lists(st.one_of(st.floats(), st.integers(), st.text()), min_size=2))

    # Ensure both lists have the same length, otherwise expect an error
    assume(len(x) == len(y))

    # Test for expected error when list length is less than 2
    assume(len(x) >= 2)

    # Calculate correlation using both methods
    pearson_corr = statistics.correlation(x, y)
    spearman_corr = statistics.correlation(x, y, method='ranked')

    # Check if correlation coefficients are within the valid range
    assert -1 <= pearson_corr <= 1
    assert -1 <= spearman_corr <= 1

# End program