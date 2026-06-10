from decimal import Decimal
from hypothesis import given, strategies as st

@given(st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_as_integer_ratio(decimal_number):
    result = Decimal(decimal_number).as_integer_ratio()
    assert isinstance(result, tuple)  # Check that the output is a tuple
    assert len(result) == 2  # Check that the tuple contains exactly two elements
    n, d = result
    assert isinstance(n, int) and isinstance(d, int)  # Check that both elements in the tuple are integers
    assert d > 0  # Check that the denominator (the second element) is positive
    # Check that dividing the numerator (the first element) by the denominator (the second) returns the original number
    assert n / d == float(decimal_number)
# End program