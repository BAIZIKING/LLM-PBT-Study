from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: We are generating a wide range of decimal numbers, including very small and large ones.
@given(st.decimals(min_value=None, max_value=None, allow_nan=False, allow_infinity=False))
def test_decimal_as_integer_ratio(decimal_value):
    # get the ratio representation
    numerator, denominator = decimal_value.as_integer_ratio()
    # Check that the ratio represents the initial value
    assert Decimal(numerator) / Decimal(denominator) == decimal_value