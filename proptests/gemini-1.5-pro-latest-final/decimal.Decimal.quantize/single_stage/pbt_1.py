from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, Context

# Summary: Generates diverse Decimal inputs for quantize, covering various precisions, scales, 
#          signs, magnitudes, and edge cases. Also tests different rounding modes and contexts.
@given(st.data())
def test_decimal_quantize(data):
    # Generate Decimal inputs
    value = data.draw(
        st.decimals(
            min_value=-1e20, max_value=1e20, allow_nan=False, allow_infinity=False
        )
    )
    exp = data.draw(
        st.decimals(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False)
    )
    rounding_mode = data.draw(st.sampled_from(list(vars(ROUND_HALF_UP).values())))
    context = data.draw(
        st.builds(
            Context,
            prec=st.integers(min_value=1, max_value=100),
            rounding=st.sampled_from(list(vars(ROUND_HALF_UP).values())),
        )
    )

    try:
        result = value.quantize(exp, rounding=rounding_mode, context=context)

        # Check exponent match
        assert result.as_tuple().exponent == exp.as_tuple().exponent

        # Check precision limitation
        assert len(str(abs(result)).replace(".", "")) <= context.prec

    except InvalidOperation:
        # Check precision overflow
        assert len(str(abs(value)).replace(".", "")) > context.prec
    except ArithmeticError as e:
        # Check exponent limits
        assert e.args[0] in ("Exponent out of range.",)

# End program