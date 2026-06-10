from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation, getcontext, ROUND_UP, ROUND_DOWN, ROUND_HALF_UP

# Summary: Generates diverse Decimal inputs and rounding modes for quantize
@given(
    x=st.decimals(
        min_value=-1e20, max_value=1e20, allow_nan=False, allow_infinity=False
    ),
    exp=st.decimals(
        min_value=-100, max_value=100, allow_nan=False, allow_infinity=False
    ),
    rounding=st.sampled_from([ROUND_UP, ROUND_DOWN, ROUND_HALF_UP]),
    context=st.builds(
        getcontext,
        prec=st.integers(min_value=1, max_value=100),
        rounding=st.sampled_from(
            [ROUND_UP, ROUND_DOWN, ROUND_HALF_UP, ROUND_HALF_EVEN]
        ),
    ),
)
def test_decimal_quantize(x, exp, rounding, context):
    # Set context for the test
    getcontext().prec = context.prec
    getcontext().rounding = context.rounding

    try:
        result = x.quantize(exp, rounding=rounding)

        # Check exponent equality
        assert result.as_tuple().exponent == exp.as_tuple().exponent

        # Check rounding behavior (comparing with expected result using string conversion is a workaround due to potential rounding differences)
        expected_result = Decimal(round(float(x), int(exp)))
        assert str(result) == str(expected_result)

    except InvalidOperation:
        # Check if error is due to precision exceeding limit
        assert len(x.as_tuple().digits) > context.prec or (
            exp.as_tuple().exponent > Decimal.max_exponent
            or exp.as_tuple().exponent < Decimal.min_exponent
        )
# End program