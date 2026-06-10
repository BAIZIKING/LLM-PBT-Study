from hypothesis import given, strategies as st
from decimal import Decimal, OverflowError, ValueError

# Summary: Generates a wide variety of Decimal inputs, including positives, negatives, varying precisions, integers, infinities, and NaNs.
@given(st.data())
def test_decimal_as_integer_ratio(data):
    # Generate Decimal inputs with different characteristics
    value = data.draw(
        st.one_of(
            st.decimals(allow_nan=True, allow_infinity=True),  # Decimals with varying precisions, including NaN and infinities
            st.integers()  # Include integers
        )
    )
    decimal_value = Decimal(value)

    # Check for expected exceptions
    if decimal_value in (Decimal('inf'), Decimal('-inf')):
        with pytest.raises(OverflowError):
            decimal_value.as_integer_ratio()
    elif decimal_value.is_nan():
        with pytest.raises(ValueError):
            decimal_value.as_integer_ratio()
    else:
        # Test normal cases
        n, d = decimal_value.as_integer_ratio()
        assert Decimal(n) / Decimal(d) == decimal_value  # Exact conversion
        assert math.gcd(n, d) == 1  # Lowest terms
        assert d > 0  # Positive denominator

# End program