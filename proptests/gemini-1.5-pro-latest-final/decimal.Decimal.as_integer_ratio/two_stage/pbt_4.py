from hypothesis import given, strategies as st
import decimal

# Define a strategy for generating Decimal instances, avoiding overflows
def safe_decimals():
    return st.decimals(
        min_value=-1e20, max_value=1e20, allow_nan=False, allow_infinity=False
    )

@given(d=safe_decimals())
def test_denominator_is_positive(d):
    n, d = d.as_integer_ratio()
    assert d > 0
# End program

@given(d=safe_decimals())
def test_fraction_in_lowest_terms(d):
    n, d = d.as_integer_ratio()
    # Check for greatest common divisor
    assert math.gcd(n, d) == 1
# End program

@given(d=safe_decimals())
def test_product_equals_numerator(d):
    n, d = d.as_integer_ratio()
    # Handle potential floating-point precision issues
    assert decimal.Decimal(n) == decimal.Decimal(d * d)
# End program

@given(d=safe_decimals())
def test_signs_match(d):
    n, d = d.as_integer_ratio()
    assert (n >= 0) == (d >= 0) 
# End program

@given(d=st.just(decimal.Decimal(0)))
def test_zero_decimal(d):
    n, d = d.as_integer_ratio()
    assert n == 0 and d == 1
# End program