from hypothesis import given, strategies as st
import decimal

# Define a strategy for generating Decimal numbers within a reasonable range to avoid overflows
decimals = st.decimals(
    min_value=-1e10, max_value=1e10, allow_nan=False, allow_infinity=False
)

@given(decimals)
def test_as_integer_ratio_type(d):
    result = d.as_integer_ratio()
    assert isinstance(result, tuple) and len(result) == 2

@given(decimals)
def test_as_integer_ratio_element_types(d):
    n, d = d.as_integer_ratio()
    assert isinstance(n, int) and isinstance(d, int)

@given(decimals)
def test_as_integer_ratio_denominator_sign(d):
    n, d = d.as_integer_ratio()
    assert d > 0

@given(decimals)
def test_as_integer_ratio_lowest_terms(d):
    n, d = d.as_integer_ratio()
    # Use math.gcd to find the greatest common divisor
    import math
    assert math.gcd(n, d) == 1

@given(decimals)
def test_as_integer_ratio_equality(d):
    n, d = d.as_integer_ratio()
    assert d != 0  # Guard against division by zero
    assert decimal.Decimal(n) / decimal.Decimal(d) == d
# End program