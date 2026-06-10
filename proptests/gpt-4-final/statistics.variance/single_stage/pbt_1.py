import statistics
from hypothesis import given, strategies as st, assume

# Test that variance is computed correctly with standard numbers, Decimal and Fraction values
@given(
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
    st.floats(allow_nan=False, allow_infinity=False).none(),
)
def test_statistics_variance_number_values(data, xbar):
    computed_variance = statistics.variance(data, xbar)
    assume(computed_variance != 0)  # Exclude degenerate case where variance == 0
    manual_variance = sum((x - xbar) ** 2 for x in data) / (len(data) - 1)
    assert computed_variance == manual_variance

# make sure that xbar parameter is optional and the output remains same
@given(
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2),
)
def test_statistics_variance_xbar_optional(data):
    computed_variance_xbar = statistics.variance(data, statistics.mean(data))
    computed_variance_no_xbar = statistics.variance(data)
    assert computed_variance_xbar == computed_variance_no_xbar

# ensure an exception is raised if data has fewer than two values
@given(
    st.lists(st.floats(allow_nan=False, allow_infinity=False), max_size=1),
    st.floats(allow_nan=False, allow_infinity=False).none(),
)
def test_statistics_variance_raising_exception(data, xbar):
    with pytest.raises(statistics.StatisticsError):
        statistics.variance(data, xbar)

# End program