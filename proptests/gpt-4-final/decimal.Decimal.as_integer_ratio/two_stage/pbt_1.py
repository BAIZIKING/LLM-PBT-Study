from hypothesis import given, strategies as st
import decimal
import math

@given(st.decimals(allow_infinity=False, allow_nan=False))
def test_as_integer_ratio_output_type(d):
    # Test 1: Output is a tuple of two integers
    ratio = decimal.Decimal(d).as_integer_ratio()
    assert isinstance(ratio, tuple)
    assert len(ratio) == 2
    assert all(isinstance(x, int) for x in ratio)

@given(st.decimals(min_value=0, max_value=1e15, allow_infinity=False, allow_nan=False))
def test_as_integer_ratio_positive_output(d):
    # Test 3: For positive decimal, both numerator and denominator should be positive
    ratio = decimal.Decimal(d).as_integer_ratio()
    assert ratio[0] > 0 and ratio[1] > 0

@given(st.decimals(min_value=-1e15, max_value=0, allow_infinity=False, allow_nan=False))
def test_as_integer_ratio_negative_output(d):
    # Test 3: For negative decimal, the numerator should be negative and the denominator should be positive
    ratio = decimal.Decimal(d).as_integer_ratio()
    assert ratio[0] < 0 and ratio[1] > 0

@given(st.decimals(allow_infinity=False, allow_nan=False))
def test_as_integer_ratio_lowest_terms(d):
    # Test 4: The result should be in lowest terms
    n, d = decimal.Decimal(d).as_integer_ratio()
    assert math.gcd(n, d) == 1

@given(st.just(decimal.Decimal('Infinity')))
def test_as_integer_ratio_overflow(d):
    # Test 5: OverflowError should be raised for infinities
    try:
        decimal.Decimal(d).as_integer_ratio()
    except OverflowError:
        assert True
    else:
        assert False

@given(st.just(decimal.Decimal('NaN')))
def test_as_integer_ratio_value_error(d):
    # Test 5: ValueError should be raised for NaNs
    try:
        decimal.Decimal(d).as_integer_ratio()
    except ValueError:
        assert True
    else:
        assert False