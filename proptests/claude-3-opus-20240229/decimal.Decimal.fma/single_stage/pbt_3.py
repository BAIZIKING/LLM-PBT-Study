from hypothesis import given, strategies as st
from decimal import Decimal, getcontext

# Summary: 
# Generate a variety of Decimal values, including:
# - Small and large magnitude positive and negative values
# - Values with different numbers of significant digits
# - Special values like 0, inf, nan, +/- inf
# - Vary precision context
# Check that fma(a, b, c) = a*b + c without intermediate rounding
@given(st.decimals(allow_nan=True, allow_infinity=True), 
       st.decimals(allow_nan=True, allow_infinity=True),
       st.decimals(allow_nan=True, allow_infinity=True),
       st.integers(min_value=1, max_value=100))
def test_decimal_fma(a, b, c, precision):
    getcontext().prec = precision
    expected = Decimal(a)*Decimal(b) + Decimal(c)
    assert expected == Decimal(a).fma(b, c)
# End program