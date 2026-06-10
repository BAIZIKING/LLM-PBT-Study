from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generates random Decimal values with edge cases and checks properties of as_integer_ratio
@given(st.data())
def test_decimal_as_integer_ratio(data):
    # Generate random Decimal inputs, including edge cases
    decimal_input = data.draw(
        st.one_of(
            st.decimals(allow_nan=True, allow_infinity=True),
            st.decimals(min_value=-1e50, max_value=1e50),
            st.just(Decimal("0.333333333333"))  # Example of repeating decimal
        )
    )

    # Handle expected errors for NaN and infinity
    if decimal_input.is_nan():
        with pytest.raises(ValueError):
            decimal_input.as_integer_ratio()
    elif decimal_input.is_infinite():
        with pytest.raises(OverflowError):
            decimal_input.as_integer_ratio()
    else:
        n, d = decimal_input.as_integer_ratio()

        # Check fraction representation
        assert Decimal(n) / Decimal(d) == decimal_input

        # Check lowest terms (using gcd)
        assert math.gcd(n, d) == 1

        # Check positive denominator
        assert d > 0

# End program