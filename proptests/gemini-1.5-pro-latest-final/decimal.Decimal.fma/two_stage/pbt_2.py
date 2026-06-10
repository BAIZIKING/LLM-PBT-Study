from hypothesis import given, strategies as st
import decimal

# Property 1: a*b+c == a.fma(b, c)
@given(a=st.decimals(allow_infinity=False, allow_nan=False),
       b=st.decimals(allow_infinity=False, allow_nan=False),
       c=st.decimals(allow_infinity=False, allow_nan=False))
def test_decimal_Decimal_fma_property_1(a, b, c):
    assert a*b+c == a.fma(b, c)

# Property 2: Output of fma should be Decimal type
@given(a=st.decimals(allow_infinity=False, allow_nan=False),
       b=st.decimals(allow_infinity=False, allow_nan=False),
       c=st.decimals(allow_infinity=False, allow_nan=False))
def test_decimal_Decimal_fma_property_2(a, b, c):
    assert isinstance(a.fma(b,c), decimal.Decimal)

# Property 3: Output of fma is integer when all inputs are integers
@given(a=st.integers(), b=st.integers(), c=st.integers())
def test_decimal_Decimal_fma_property_3(a, b, c):
    assert isinstance(decimal.Decimal(a).fma(b, c), int)

# Property 4: 0*b+c == c
@given(b=st.decimals(allow_infinity=False, allow_nan=False),
       c=st.decimals(allow_infinity=False, allow_nan=False))
def test_decimal_Decimal_fma_property_4(b, c):
    assert decimal.Decimal(0).fma(b, c) == c

# Property 5: a*b+0 == a*b 
@given(a=st.decimals(allow_infinity=False, allow_nan=False),
       b=st.decimals(allow_infinity=False, allow_nan=False))
def test_decimal_Decimal_fma_property_5(a, b):
    assert a.fma(b, 0) == a*b
# End program