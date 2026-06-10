from hypothesis import given, strategies as st
from decimal import Decimal

# Test for Property 1
@given(st.floats(allow_nan=False, allow_infinity=False))
def test_decimal_instance(test_input):
    result = Decimal.from_float(test_input)
    assert isinstance(result, Decimal), "Output is not Decimal instance"

# Test for Property 2
def test_nan_conversion():
    result = Decimal.from_float(float('nan'))
    assert result.is_nan(), "NaN was not converted correctly"

# Test for Property 3 positive infinity
def test_pos_infinity_conversion():
    result = Decimal.from_float(float('inf'))
    assert result.is_infinite() and not result.is_signed(), "Positive infinity was not converted correctly"

# Test for Property 3 negative infinity
def test_neg_infinity_conversion():
    result = Decimal.from_float(float('-inf'))
    assert result.is_infinite() and result.is_signed(), "Negative infinity was not converted correctly"

# Test for Property 4
@given(st.floats(allow_nan=False, allow_infinity=False, min_value=0.1, max_value=0.1))
def test_accurate_floating_point_conversion(test_input):
    approx_result = Decimal.from_float(test_input)
    exact_result = Decimal(str(test_input))
    assert approx_result != exact_result, "Floating point number was not converted accurately"

# Test for Property 5
@given(st.integers())
def test_exact_integer_conversion(test_input):
    result = Decimal.from_float(test_input)
    expected = Decimal(str(test_input))
    assert result == expected, "Integer was not converted exactly"
# End program