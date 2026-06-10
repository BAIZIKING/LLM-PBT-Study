from hypothesis import given, strategies as st
import statistics

# Summary: The generation strategy aims to create a diverse range of inputs for the statistics.variance function, encompassing various data types, lengths, and potential edge cases.

# 1. Data Generation:
#   - Data Type: We employ st.one_of to include various numerical data types: integers, floats, decimals, and fractions.
#   - Data Length: st.lists is used to generate lists of varying lengths, including empty lists and lists with only one element to test edge cases. 

@given(st.data())
def test_statistics_variance(data):
    # Draw a list of numbers with varying types and lengths
    data_list = data.draw(
        st.lists(
            st.one_of(
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),  # Exclude NaN and infinity
                st.decimals(),
                st.fractions()
            ),
            min_size=0,  # Allow empty lists
        )
    )

    # 2. Edge Case Handling:
    #   - Empty List: If the list is empty, statistics.variance should raise a StatisticsError.
    if not data_list:
        with pytest.raises(statistics.StatisticsError):
            statistics.variance(data_list)
        return

    #   - Single Element: If the list has only one element, statistics.variance should return 0.
    if len(data_list) == 1:
        assert statistics.variance(data_list) == 0
        return

    # 3. Property Verification:
    #   - Non-negativity: The variance should always be non-negative.
    assert statistics.variance(data_list) >= 0

    #   - Calculation with Mean: If the mean is provided, the result should be the same as calculating without it. 
    mean_value = statistics.mean(data_list)
    assert statistics.variance(data_list, mean_value) == statistics.variance(data_list)
# End program