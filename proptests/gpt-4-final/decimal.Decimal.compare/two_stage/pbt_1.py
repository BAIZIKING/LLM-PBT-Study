from hypothesis import given, strategies as st
import decimal

@given(st.floats(allow_nan=False), st.floats(allow_nan=False))
def test_NaN_property(a, b):
    x = decimal.Decimal(a)
    y = decimal.Decimal(b)
    assert x.compare(decimal.Decimal('NaN')).is_nan()
    assert decimal.Decimal('NaN').compare(y).is_nan()

@given(st.tuples(st.floats(allow_nan=False), st.floats(allow_nan=False)).filter(lambda x: x[0] < x[1]))
def test_less_than_property(a, b):
    x = decimal.Decimal(a)
    y = decimal.Decimal(b)
    assert x.compare(y) == decimal.Decimal('-1')

@given(st.floats(allow_nan=False))
def test_equal_property(a):
    x = decimal.Decimal(a)
    y = decimal.Decimal(a)
    assert x.compare(y) == decimal.Decimal('0')

@given(st.tuples(st.floats(allow_nan=False), st.floats(allow_nan=False)).filter(lambda x: x[0] > x[1]))
def test_greater_than_property(a, b):
    x = decimal.Decimal(a)
    y = decimal.Decimal(b)
    assert x.compare(y) == decimal.Decimal('1')

@given(st.tuples(st.floats(allow_nan=False), st.floats(allow_nan=False)).filter(lambda x: x[0] != x[1]))
def test_commutative_property(a, b):
    x = decimal.Decimal(a)
    y = decimal.Decimal(b)
    assert x.compare(y) == -y.compare(x)