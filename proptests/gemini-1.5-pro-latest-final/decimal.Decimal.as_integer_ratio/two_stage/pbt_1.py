from hypothesis import given, strategies as st
import decimal

# Define a strategy for generating Decimal instances, avoiding overflows
def safe_decimals():
    return st.decimals(
        allow_nan=False, allow_infinity=False, min_value=-1e20, max_value=1e20
    )

@given(safe_decimals())
def test_denominator_is_positive(dec):
    n, d = dec.as_integer_ratio()
    assert d > 0
# End program

@given(safe_decimals())
def test_fraction_in_lowest_terms(dec):
    n, d = dec.as_integer_ratio()
    assert math.gcd(n, d) == 1
# End program

@given(safe_decimals())
def test_product_equals_numerator(dec):
    n, d = dec.as_integer_ratio()
    # Use a higher precision context to avoid rounding errors
    with decimal.localcontext() as ctx:
        ctx.prec += 2
        result = (dec * d) / n
    assert result == decimal.Decimal(n) 
# End program

@given(safe_decimals())
def test_signs_match(dec):
    n, d = dec.as_integer_ratio()
    assert (dec.is_signed() == (n < 0))
# End program

@given(safe_decimals())
def test_roundtrip(dec):
    n, d = dec.as_integer_ratio()
    new_dec = decimal.Decimal(n) / decimal.Decimal(d)
    n2, d2 = new_dec.as_integer_ratio()
    assert n == n2 and d == d2
# End program