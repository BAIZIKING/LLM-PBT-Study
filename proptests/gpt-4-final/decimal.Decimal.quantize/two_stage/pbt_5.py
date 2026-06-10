from hypothesis import given, strategies as st
import decimal

@given(st.decimals(),st.decimals())
def test_decimal_quantize_property1(decimal1, decimal2):
    result = decimal1.quantize(decimal2)
    assert result.as_tuple().exponent == decimal2.as_tuple().exponent

@given(st.decimals(),st.decimals())
def test_decimal_quantize_property2(decimal1, decimal2):
    try:
        decimal1.quantize(decimal2)
    except decimal.Underflow:
        assert False, "Underflow exception raised"

@given(st.decimals(),st.decimals())
def test_decimal_quantize_property3(decimal1, decimal2):
    initial_exponent = decimal1.as_tuple().exponent
    if initial_exponent < decimal2.as_tuple().exponent:
        result = decimal1.quantize(decimal2)
        assert result >= decimal1 and result <= decimal1 + 10**(initial_exponent-decimal2.as_tuple().exponent)

@given(st.decimals(),st.decimals())
def test_decimal_quantize_property4(decimal1, decimal2):
    try:
        result = decimal1.quantize(decimal2)
        assert len(str(result).split('.')[-1]) <= decimal.getcontext().prec
    except decimal.InvalidOperation:
        pass

@given(st.decimals(),st.decimals())
def test_decimal_quantize_property5(decimal1, decimal2):
    try:
        decimal1.quantize(decimal2)
    except decimal.InvalidOperation as error:
        if "exponent out of bounds" in str(error):
            pass
        else:
            assert False, "Unexpected error raised"

# End program