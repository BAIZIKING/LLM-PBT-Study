from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation

@given(st.decimals(allow_nan=True), st.decimals(allow_nan=True))
def test_decimal_compare_property_NaN(a, b):
    try:
        c = a.compare(b)
    except InvalidOperation:
        assert a.is_nan() or b.is_nan()
    else:
        assert not (a.is_nan() or b.is_nan())

@given(st.decimals(allow_nan=False))
def test_decimal_compare_property_equal(a):
    assert a.compare(a) == 0

@given(st.tuples(st.decimals(allow_nan=False), st.decimals(allow_nan=False)).filter(lambda x: x[0] < x[1]))
def test_decimal_compare_property_less(inputs):
    a, b = inputs
    assert a.compare(b) == -1

@given(st.tuples(st.decimals(allow_nan=False), st.decimals(allow_nan=False)).filter(lambda x: x[0] > x[1]))
def test_decimal_compare_property_greater(inputs):
    a, b = inputs
    assert a.compare(b) == 1

@given(st.tuples(st.decimals(allow_nan=False), st.decimals(allow_nan=False)).filter(lambda x: x[0] != x[1]))
def test_decimal_compare_property_commutative(inputs):
    a, b = inputs
    assert a.compare(b) == -b.compare(a)