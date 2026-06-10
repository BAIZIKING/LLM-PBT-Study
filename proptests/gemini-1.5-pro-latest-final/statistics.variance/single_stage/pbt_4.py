from hypothesis import given, strategies as st
from statistics import variance, mean
from decimal import Decimal
from fractions import Fraction

# Summary: Generates diverse data types, sizes, and distributions to test variance calculation.
@given(
    st.data()
)
def test_statistics_variance(data):
    # Generate data with varying types and sizes
    input_data = data.draw(
        st.one_of(
            st.lists(st.floats(allow_nan=True), min_size=2),
            st.lists(st.decimals(allow_nan=True), min_size=2),
            st.lists(st.fractions(), min_size=2),
        )
    )

    # Test calculation accuracy
    calculated_variance = variance(input_data)
    manual_variance = sum((x - mean(input_data))**2 for x in input_data) / (len(input_data) - 1)
    assert abs(calculated_variance - manual_variance) < 1e-10  # Account for potential floating-point errors

    # Test mean handling
    if not any(math.isnan(x) for x in input_data):  # Calculate mean only if no NaN values
        calculated_mean = mean(input_data)
        assert variance(input_data, xbar=calculated_mean) == calculated_variance

    # Test error handling
    with pytest.raises(StatisticsError):
        variance(input_data[:1])  # Test with less than two elements

    # Test data type consistency
    if all(isinstance(x, Decimal) for x in input_data):
        assert isinstance(calculated_variance, Decimal)
    elif all(isinstance(x, Fraction) for x in input_data):
        assert isinstance(calculated_variance, Fraction)

# End program