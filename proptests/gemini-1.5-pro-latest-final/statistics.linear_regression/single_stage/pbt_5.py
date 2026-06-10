from hypothesis import given, strategies as st
import statistics

# Summary: The generation strategy aims to create a wide variety of inputs for the `statistics.linear_regression` function, including both valid and edge cases. 
# It generates lists of floats for both `x` and `y`, ensuring they have the same length (at least 2). The strategy also considers cases with constant `x` values 
# to trigger the expected `StatisticsError`. Additionally, it explores different magnitudes and distributions of values to test the robustness of the function.

@given(st.data())
def test_statistics_linear_regression(data):
    # Generate lists of floats with the same length
    list_length = data.draw(st.integers(min_value=2, max_value=100))
    x = data.draw(st.lists(st.floats(), min_size=list_length, max_size=list_length))
    y = data.draw(st.lists(st.floats(), min_size=list_length, max_size=list_length))

    # Introduce edge case: constant x values
    if data.draw(st.booleans()):
        constant_value = data.draw(st.floats())
        x = [constant_value] * list_length

    # Test cases with different magnitudes and distributions
    x = data.draw(st.one_of(
        st.lists(st.floats(allow_nan=False, allow_infinity=False)),  # Regular floats
        st.lists(st.floats(min_value=-1e10, max_value=1e10)),      # Large magnitudes
        st.lists(st.floats(min_value=0, max_value=1e-6))           # Small magnitudes 
    ))

    # Check for expected StatisticsError when x is constant
    if all(v == x[0] for v in x):
        with pytest.raises(statistics.StatisticsError):
            statistics.linear_regression(x, y)
    else:
        # Check that the function returns a tuple of two floats (slope and intercept)
        result = statistics.linear_regression(x, y)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], float)
        assert isinstance(result[1], float)

# End program