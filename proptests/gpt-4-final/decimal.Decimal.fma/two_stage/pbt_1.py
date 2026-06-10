from hypothesis import given, strategies as st
import decimal

@given(st.decimals(), st.decimals(), st.decimals())
def test_type_of_output(a, b, c):
    assert isinstance(decimal.Decimal(a).fma(b, c), decimal.Decimal)

@given(st.decimals(), st.decimals())
def test_missing_third_argument(a, b):
    try:
        decimal.Decimal(a).fma(b)
        assert False
    except TypeError:
        assert True

@given(st.decimals(), st.decimals(), st.decimals())
def test_commutativity(a, b, c):
    assert decimal.Decimal(a).fma(b, c) != decimal.Decimal(a).fma(c, b)

@given(st.decimals(), st.decimals())
def test_distributive_property(a, b):
    assert decimal.Decimal(a).fma(b, 0) == a * b

@given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_inputs(a, b, c):
    try:
        decimal.Decimal(a).fma(b, c)
        assert True
    except:
        assert False
# End program