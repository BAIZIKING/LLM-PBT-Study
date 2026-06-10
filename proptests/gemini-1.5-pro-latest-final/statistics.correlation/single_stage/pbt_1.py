from hypothesis import given, strategies as st

# Summary: Generates diverse list pairs with varying data types, lengths, 
#          and constant values to test correlation calculations and error handling.
@given(
    st.data(),
    st.booleans(),  # To choose between 'linear' and 'ranked' methods
    st.one_of(st.floats(), st.integers(), st.text(), st.none()),  # Data types
)
def test_statistics_correlation(data, use_ranked_method, data_type):
    method = "ranked" if use_ranked_method else "linear"

    # Generate lists with varying lengths and potentially different lengths
    x_len = data.draw(st.integers(min_value=0, max_value=100))
    y_len = data.draw(st.integers(min_value=0, max_value=100))

    # Create strategies for list elements based on chosen data type
    if data_type is None:
        element_strategy = st.none()
    elif data_type is float:
        element_strategy = st.floats(allow_nan=False)  # Avoid NaN values
    elif data_type is int:
        element_strategy = st.integers()
    else:  # data_type is str
        element_strategy = st.text()

    x = data.draw(st.lists(element_strategy, min_size=x_len, max_size=x_len))
    y = data.draw(st.lists(element_strategy, min_size=y_len, max_size=y_len))

    # Test error handling for length mismatch or less than two elements
    if x_len != y_len or x_len < 2 or y_len < 2:
        with pytest.raises(StatisticsError):
            statistics.correlation(x, y, method=method)
        return

    # Test data type handling and correlation value range
    try:
        correlation = statistics.correlation(x, y, method=method)
        assert -1 <= correlation <= 1
    except TypeError:
        # TypeError expected for non-numeric data
        assert data_type is not None and not isinstance(data_type, (int, float))

# End program