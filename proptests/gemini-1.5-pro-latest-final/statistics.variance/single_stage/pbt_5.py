from hypothesis import given, strategies as st
import statistics

# Summary: The strategy aims to generate a wide variety of inputs for the statistics.variance function, including:
# - Varied lengths of data: Lists with varying sizes to test behavior with different amounts of data.
# - Diverse data types: Includes integers, floats, Fractions, and Decimals to ensure compatibility.
# - Edge cases: Empty lists and lists with only one element to check for expected errors.
# - Presence and absence of xbar: Tests cases with and without a pre-calculated mean. 
@given(st.data())
def test_statistics_variance(data):
    # Generate data for testing
    data_list = data.draw(
        st.lists(
            st.one_of(
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.decimals(allow_nan=False, allow_infinity=False),
                st.fractions()
            ),
            min_size=0,
            max_size=100
        )
    )

    # Test cases based on data length
    if len(data_list) < 2:
        with pytest.raises(statistics.StatisticsError):
            statistics.variance(data_list)
    else:
        # Calculate variance with and without pre-calculated mean
        result1 = statistics.variance(data_list)
        mean_value = statistics.mean(data_list)
        result2 = statistics.variance(data_list, xbar=mean_value)

        # Check properties
        assert isinstance(result1, (int, float, Decimal, Fraction))  # Ensure correct return type
        assert result1 >= 0  # Variance should be non-negative 
        assert result1 == result2  # Results with and without xbar should match

# End program