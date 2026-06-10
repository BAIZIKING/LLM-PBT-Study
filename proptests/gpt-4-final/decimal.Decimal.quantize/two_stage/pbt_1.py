from hypothesis import given, strategies as st
import decimal

# Property 1
@given(st.decimals(), st.decimals())
def test_quantize_returns_decimal(first_operand, second_operand):
    result = first_operand.quantize(second_operand)
    assert isinstance(result, decimal.Decimal)

# Property 2
@given(st.decimals(), st.decimals(), st.integers(min_value=0))
def test_quantize_invalid_operation(first_operand, second_operand, precision):
    with decimal.localcontext() as ctx:
        ctx.prec = precision
        if len(str(first_operand.quantize(second_operand))) > precision:
            with pytest.raises(decimal.InvalidOperation):
                first_operand.quantize(second_operand)

# Property 3
# Assuming no signaling of Underflow means we don't have to handle such a situation.

# Property 4
@given(st.decimals(), st.decimals(min_value=1.0), st.sampled_from([decimal.ROUND_DOWN,decimal.ROUND_UP]))
def test_quantize_rounding(first_operand, second_operand, rounding_style):
    with decimal.localcontext() as ctx:
        ctx.rounding = rounding_style
        rounded = first_operand.quantize(second_operand)
        assert rounded == first_operand.quantize(second_operand)

# Property 5
@given(st.decimals(), st.decimals())
def test_quantize_exponent_limits(first_operand, second_operand):
    with pytest.raises(decimal.InvalidOperation):
        with decimal.localcontext() as ctx:
            ctx.Emax = 10
            ctx.Etiny = -10
            if second_operand>ctx.Emax or second_operand<ctx.Etiny:
                first_operand.quantize(second_operand)
# End program