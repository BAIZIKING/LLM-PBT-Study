from hypothesis import given, strategies as st
from decimal import Decimal
import math

# Property 1: Consistency Property
@given(st.floats())
def test_consistency_property(f):
    assert Decimal.from_float(f) == Decimal.from_float(f)

# Property 2: Limit Property
@given(st.just(float('inf')))
def test_limit_property_positive_infinity(f):
    assert Decimal.from_float(f) == Decimal('Infinity')

@given(st.just(float('-inf')))
def test_limit_property_negative_infinity(f):
    assert Decimal.from_float(f) == Decimal('-Infinity')

# Property 3: Approximation property 
@given(st.floats())
def test_approximation_property(f):
    assert abs(float(Decimal.from_float(f)) - f) < 1e-10

# Property 4: Invalid Values
@given(st.just(float('nan')))
def test_invalid_value_property(f):
    assert math.isnan(Decimal.from_float(f))

# Property 5: Type Property
@given(st.floats() | st.integers())
def test_type_property(n):
    assert isinstance(Decimal.from_float(n), Decimal)