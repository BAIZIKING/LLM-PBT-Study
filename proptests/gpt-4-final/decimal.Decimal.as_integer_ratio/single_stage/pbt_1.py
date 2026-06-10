from hypothesis import given, strategies as st
from decimal import Decimal

@given(st.decimals(min_value=-1e20, max_value=1e20, allow_nan=False, allow_infinity=False))
def test_decimal_as_integer_ratio(decimal_value):
    # The decimals strategy generates finite decimal floating-point numbers. We then use those as input for the as_integer_ratio() method
    n, d = Decimal(decimal_value).as_integer_ratio()

    # Check the output is a pair (tuple) of integers
    assert isinstance(n, int) and isinstance(d, int)

    # Check that n/d is exactly equal to the input value, this tests the accuracy of the conversion.
    assert Decimal(n) / Decimal(d) == Decimal(decimal_value)