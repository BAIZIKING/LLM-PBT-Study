from hypothesis import given, strategies as st
import statistics

# Summary: The generation strategy aims to create a diverse set of inputs for the statistics.variance function, including:
# - Varied lengths of data: Lists with varying sizes to test the behavior with different data set sizes.
# - Different data types: Lists containing integers, floats, and a mix of both to assess handling of various numerical types.
# - Edge cases: Lists with the minimum required length (2) and lists containing identical values to check for correct variance calculation in these situations.
@given(
    st.lists(
        elements=st.one_of(st.integers(), st.floats()),
        min_size=2,
        max_size=100,
    ),
    st.one_of(st.none(), st.floats()),
)
def test_statistics_variance(data, xbar):
    # Property 1: Check if the calculated variance is non-negative. Variance, being a measure of dispersion, should always be greater than or equal to zero.
    result = statistics.variance(data, xbar)
    assert result >= 0

    # Property 2: If xbar (mean) is provided, ensure it matches the calculated mean of the data.
    if xbar is not None:
        assert xbar == statistics.mean(data)

    # Property 3: For data with identical values, the variance should be zero.
    if all(x == data[0] for x in data):
        assert result == 0
# End program