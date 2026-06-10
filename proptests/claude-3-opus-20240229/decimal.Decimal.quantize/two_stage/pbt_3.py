from hypothesis import given, strategies as st
import decimal

@given(
    value=st.decimals(allow_nan=False, allow_infinity=False),
    exp=st.decimals(allow_nan=False, allow_infinity=False),
    rounding=st.sampled_from([None] + list(decimal.ROUND_MODES.values())),
    context=st.builds(decimal.Context)
)
def test_decimal_quantize_property(value, exp, rounding, context):
    try:
        result = value.quantize(exp, rounding=rounding, context=context)
        assert result.as_tuple().exponent == exp.as_tuple().exponent
        assert len(result.as_tuple().digits) <= context.prec
        if rounding is not None:
            assert result == value.quantize(exp, rounding=rounding)
        else:
            assert result == value.quantize(exp, context=context)
    except (decimal.InvalidOperation, decimal.Overflow, decimal.Underflow):
        min_exp = context.Etiny()
        max_exp = context.Emax()
        assert exp.as_tuple().exponent < min_exp or exp.as_tuple().exponent > max_exp

@given(
    value=st.decimals(allow_nan=False, allow_infinity=False),
    exp=st.decimals(allow_nan=False, allow_infinity=False)
)
def test_decimal_quantize_value(value, exp):
    try:
        result = value.quantize(exp)
        rounded_value = decimal.Decimal(value).quantize(exp)
        assert result == rounded_value
    except (decimal.InvalidOperation, decimal.Overflow, decimal.Underflow):
        pass
# End program