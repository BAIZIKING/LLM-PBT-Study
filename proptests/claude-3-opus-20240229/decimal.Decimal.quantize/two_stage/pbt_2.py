from hypothesis import given, strategies as st
import decimal

@given(st.decimals(allow_nan=False, allow_infinity=False), st.integers(min_value=-100, max_value=100))
def test_decimal_quantize_exponent(val, exp):
    quantized = val.quantize(decimal.Decimal(10) ** decimal.Decimal(exp))
    assert quantized.as_tuple().exponent == exp

@given(st.decimals(allow_nan=False, allow_infinity=False), st.integers(min_value=-100, max_value=100))
def test_decimal_quantize_rounding(val, exp):
    precision = abs(exp)
    quantized = val.quantize(decimal.Decimal(10) ** decimal.Decimal(exp))
    assert quantized == round(val, precision)

@given(st.decimals(allow_nan=False, allow_infinity=False), st.integers(max_value=-100))
def test_decimal_quantize_invalid_operation(val, exp):
    context = decimal.getcontext()
    context.prec = 5
    with decimal.localcontext(context):
        try:
            val.quantize(decimal.Decimal(10) ** decimal.Decimal(exp))
        except decimal.InvalidOperation:
            assert True
        else:
            assert False

@given(st.decimals(allow_nan=False, allow_infinity=False), st.integers(min_value=-100, max_value=100))
def test_decimal_quantize_no_underflow(val, exp):
    try:
        quantized = val.quantize(decimal.Decimal(10) ** decimal.Decimal(exp))
    except decimal.Underflow:
        assert False
    else:
        assert True

@given(st.decimals(allow_nan=False, allow_infinity=False), st.integers(max_value=decimal.getcontext().Emin - 1))
def test_decimal_quantize_exponent_error_etiny(val, exp):
    try:
        val.quantize(decimal.Decimal(10) ** decimal.Decimal(exp))
    except (decimal.InvalidOperation, decimal.Overflow, decimal.Underflow):
        assert True
    else:
        assert False

@given(st.decimals(allow_nan=False, allow_infinity=False), st.integers(min_value=decimal.getcontext().Emax + 1))
def test_decimal_quantize_exponent_error_emax(val, exp):
    try:
        val.quantize(decimal.Decimal(10) ** decimal.Decimal(exp))
    except (decimal.InvalidOperation, decimal.Overflow, decimal.Underflow):
        assert True
    else:
        assert False
# End program