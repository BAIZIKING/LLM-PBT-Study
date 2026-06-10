from hypothesis import given, strategies as st
import decimal

# Define a strategy for generating floats, including NaN and infinities
floats = st.floats(allow_nan=True, allow_infinity=True)

@given(floats)
def test_output_is_decimal_instance(f):
    result = decimal.Decimal.from_float(f)
    assert isinstance(result, decimal.Decimal)

@given(st.just(float('nan')))
def test_nan_preserved(nan_value):
    result = decimal.Decimal.from_float(nan_value)
    assert result.is_nan()

@given(st.just(float('inf')))
def test_positive_infinity_preserved(inf_value):
    result = decimal.Decimal.from_float(inf_value)
    assert result.is_infinite() and not result.is_negative()

@given(st.just(float('-inf')))
def test_negative_infinity_preserved(neg_inf_value):
    result = decimal.Decimal.from_float(neg_inf_value)
    assert result.is_infinite() and result.is_negative()

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_finite_floats_have_exact_decimal_representation(finite_float):
    result = decimal.Decimal.from_float(finite_float)
    assert float(result) == finite_float

@given(st.integers())
def test_integer_input_yields_exact_decimal(int_value):
    result = decimal.Decimal.from_float(int_value)
    assert result == decimal.Decimal(int_value)

# Testing immutability is more complex and would likely involve introspection
# or attempting to modify the Decimal object and checking for errors. 
# It's omitted here for brevity and focus on the core properties.