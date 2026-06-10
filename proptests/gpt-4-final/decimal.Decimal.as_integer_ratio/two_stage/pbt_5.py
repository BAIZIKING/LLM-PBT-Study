from hypothesis import given, strategies as st
import decimal
import math

# Test strategy: We generate random floating point numbers and convert them to Decimal instances.
# The reason is that it is simpler to generate floating points than decimals directly.

@st.composite
def decimals(draw):
    f = draw(st.floats(allow_nan=False, allow_infinity=False))
    return decimal.Decimal(str(f))

@given(decimals())
def test_output_is_pair_of_integers(d):
    numerator, denominator = d.as_integer_ratio()
    assert isinstance(numerator, int)
    assert isinstance(denominator, int)

@given(decimals())
def test_ratio_is_exact(d):
    numerator, denominator = d.as_integer_ratio()
    assert decimal.Decimal(numerator) / decimal.Decimal(denominator) == d

@given(decimals())
def test_output_is_in_lowest_terms(d):
    numerator, denominator = d.as_integer_ratio()
    assert math.gcd(numerator, denominator) == 1

@given(decimals())
def test_denominator_is_positive(d):
    _, denominator = d.as_integer_ratio()
    assert denominator > 0

@given(st.just(decimal.Decimal('NaN')))
def test_raises_on_nan(d):
    try:
        d.as_integer_ratio()
        assert False, "Expected ValueError"
    except ValueError:
        pass

@given(st.floats(allow_nan=False, allow_infinity=True).map(decimal.Decimal))
def test_raises_on_infinities(d):
    try:
        d.as_integer_ratio()
        assert False, "Expected OverflowError"
    except OverflowError:
        pass
# End program
