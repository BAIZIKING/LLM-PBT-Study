from hypothesis import given, strategies as st
from decimal import Decimal

@given(
    self=st.decimals(min_value=-1e100, max_value=1e100, allow_nan=False, allow_infinity=False),
    other=st.decimals(min_value=-1e100, max_value=1e100, allow_nan=False, allow_infinity=False),
    third=st.decimals(min_value=-1e100, max_value=1e100, allow_nan=False, allow_infinity=False)
)
def test_decimal_fma(self, other, third):
    fma_result = self.fma(other, third)

    # check type
    assert isinstance(fma_result, Decimal)
    
    # check calculation
    assert fma_result == (self * other) + third

    # special case where other and third are zero
    if other == 0 and third == 0:
        assert fma_result == 0
# End program