from hypothesis import given, strategies as st
from decimal import Decimal

# Property 1: Output is of type Decimal
@given(st.floats())
def test_output_type(f):
    result = Decimal.from_float(f)
    assert isinstance(result, Decimal)

# Property 2: Output is an equivalent decimal
@given(st.just(0.1))
def test_decimal_equivalency(f):
    result = Decimal.from_float(f)
    assert result == Decimal('0.1000000000000000055511151231257827021181583404541015625')

# Property 3: Output is 'NaN' when input is 'nan'
@given(st.just(float('nan')))
def test_nan_input(f):
    result = Decimal.from_float(f)
    assert result == Decimal('NaN')

# Property 4: Output is 'Infinity' when input is 'inf'
@given(st.just(float('inf')))
def test_inf_input(f):
    result = Decimal.from_float(f)
    assert result == Decimal('Infinity')

# Property 5: Output is '-Infinity' when input is '-inf'
@given(st.just(float('-inf')))
def test_neg_inf_input(f):
    result = Decimal.from_float(f)
    assert result == Decimal('-Infinity')