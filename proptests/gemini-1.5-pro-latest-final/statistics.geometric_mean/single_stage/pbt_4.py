from hypothesis import given, strategies as st
import statistics

# Summary: Generates various data structures with positive floats and checks for non-empty input and positive geometric mean.
@given(st.data())
def test_statistics_geometric_mean(data):
    data_list = data.draw(
        st.lists(st.floats(min_value=1), min_size=1)
    )  # Generate list of positive floats, ensuring non-empty
    assert data_list  # Check for non-empty input

    expected_mean = 1
    for x in data_list:
        expected_mean *= x
    expected_mean **= 1 / len(data_list)

    result = statistics.geometric_mean(data_list)
    assert result > 0  # Check for positive geometric mean
    assert abs(result - expected_mean) < 1e-6  # Account for potential floating-point errors
# End program