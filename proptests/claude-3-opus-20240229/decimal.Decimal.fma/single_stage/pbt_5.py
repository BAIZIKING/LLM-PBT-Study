from hypothesis import given, strategies as st
from decimal import Decimal, getcontext

# Generate a wide variety of Decimal inputs, including:
# - Positive and negative values
# - Values with different precisions 
# - Special values like 0, inf, nan
# Also generate some decimal contexts with different precision, rounding, etc.
@given(
    st.decimals(allow_nan=True, allow_infinity=True), 
    st.decimals(allow_nan=True, allow_infinity=True),
    st.decimals(allow_nan=True, allow_infinity=True),
    st.builds(getcontext)
)
def test_decimal_fma(self, other, third, context):
    # Set the decimal context for this test
    getcontext().prec = context.prec 
    getcontext().rounding = context.rounding

    # Compute fused multiply-add 
    result = self.fma(other, third)

    # Check that result matches self*other + third
    assert result == self*other + third

    # Check that precision of result matches precision of input context
    assert result.as_tuple().exponent == -context.prec

# End program