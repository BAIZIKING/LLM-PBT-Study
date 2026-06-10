from decimal import Decimal
from hypothesis import given, assume, strategies as st

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_fma_property_1(d1,d2,d3):
    result = d1.fma(d2,d3)
    assert result>=0

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_fma_property_2(d1,d2):
    result = d1.fma(d2,0)
    assert result == d1*d2

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_fma_property_3(d1,d3):
    result = d1.fma(1,d3)
    assert result == d1+d3

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_fma_property_4(d1,d2,d3):
    assume(d2 != d3)
    result1 = d1.fma(d2,d3)
    result2 = d1.fma(d3,d2)
    assert result1 != result2

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.tuples(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False)).filter(lambda x:x[0]<x[1]))
def test_decimal_fma_property_5(d1,d2,tuple_third):
    result1 = d1.fma(d2,tuple_third[0])
    result2 = d1.fma(d2,tuple_third[1])
    assert result1 < result2
# End program