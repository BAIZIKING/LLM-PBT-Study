from hypothesis import given, strategies as st
from decimal import Decimal, localcontext

# Summary: Generate three finite, bounded Decimals (self, other, third) with varied
# precision and exponents. Under a high-precision context, verify that
# self.fma(other, third) == self*other + third (intermediate product unrounded).
@given(st.data())
def test_decimal_Decimal_fma():
    data = st.data()  # placeholder to satisfy format; real draws below

    finite_decimals = st.decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=Decimal("-1e50"),
        max_value=Decimal("1e50"),
        places=None,
    )

    @given(self_val=finite_decimals, other=finite_decimals, third=finite_decimals)
    def inner(self_val, other, third):
        # Use a high-precision context so the exact product is not rounded,
        # allowing an exact comparison between fma and the manual computation.
        with localcontext() as ctx:
            ctx.prec = 200  # large enough to hold exact intermediate product + add
            fma_result = self_val.fma(other, third)
            reference = self_val * other + third
            assert fma_result == reference

    inner()
# End program