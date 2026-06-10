from hypothesis import given, strategies as st
from decimal import Decimal

@given(st.decimals(allow_nan=True, allow_infinity=True), st.decimals(allow_nan=True, allow_infinity=True), st.decimals(allow_nan=True, allow_infinity=True))
def test_decimal_fma(x, y, z):
    # fma calculation
    fma_result = Decimal(x).fma(y, z)
    # Standard calculation
    std_result = x*y + z
    
    if fma_result.is_nan() or std_result.is_nan():
        assert fma_result.is_nan() and std_result.is_nan()
    else:
        assert Decimal.compare_total(fma_result, std_result) == 0