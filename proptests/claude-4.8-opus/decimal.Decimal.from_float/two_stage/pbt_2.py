from hypothesis import given, strategies as st
import decimal
import math
from decimal import Decimal


@given(st.one_of(
    st.floats(),
    st.integers(min_value=-10**50, max_value=10**50),
))
def test_decimal_Decimal_from_float_type_preservation(f):
    # Property 1: Output is always a Decimal instance.
    result = Decimal.from_float(f)
    assert isinstance(result, Decimal)


@given(st.integers(min_value=-10**50, max_value=10**50))
def test_decimal_Decimal_from_float_integer_equivalence(n):
    # Property 2: For integer inputs, the result equals that integer value.
    result = Decimal.from_float(n)
    assert result == Decimal(n)


@given(st.sampled_from([
    (float('nan'), 'NaN'),
    (float('inf'), 'Infinity'),
    (float('-inf'), '-Infinity'),
]))
def test_decimal_Decimal_from_float_special_values(pair):
    # Property 3: Special float values map to the corresponding Decimal.
    f, expected = pair
    result = Decimal.from_float(f)
    if math.isnan(f):
        assert result.is_nan()
    else:
        assert result == Decimal(expected)


@given(st.floats(allow_nan=False, allow_infinity=False))
def test_decimal_Decimal_from_float_round_trip(f):
    # Property 4: Converting the Decimal back to float yields the original float.
    result = Decimal.from_float(f)
    assert float(result) == f


@given(st.floats(allow_nan=False, allow_infinity=False))
def test_decimal_Decimal_from_float_sign_consistency(f):
    # Property 5: Sign of the output matches the sign of the input.
    result = Decimal.from_float(f)
    # math.copysign(1.0, f) is -1.0 for negative (incl. -0.0), else 1.0
    input_negative = math.copysign(1.0, f) < 0
    output_negative = result.is_signed()
    assert input_negative == output_negative
# End program