from hypothesis import given, strategies as st
from decimal import Decimal, localcontext

# Summary: Generate three finite, bounded, low-precision decimals (no NaN/Inf) so
# that the exact product self*other and the final sum stay within the default
# precision. Verify that self.fma(other, third) equals self*other+third computed
# exactly in a high-precision context (where the intermediate product is exact).
@given(st.data())
def test_decimal_Decimal_fma(data):
    finite_decimals = st.decimals(
        min_value=Decimal("-1e10"),
        max_value=Decimal("1e10"),
        allow_nan=False,
        allow_infinity=False,
        places=6,
    )
    self_val = data.draw(finite_decimals)
    other = data.draw(finite_decimals)
    third = data.draw(finite_decimals)

    fma_result = self_val.fma(other, third)

    # Compute the reference exactly: high precision makes the intermediate
    # product self_val*other exact, mirroring fma's "no rounding" semantics.
    with localcontext() as ctx:
        ctx.prec = 80
        expected = self_val * other + third

    assert fma_result == expected, (
        f"fma({self_val}, {other}, {third}) = {fma_result}, "
        f"expected {expected}"
    )
# End program