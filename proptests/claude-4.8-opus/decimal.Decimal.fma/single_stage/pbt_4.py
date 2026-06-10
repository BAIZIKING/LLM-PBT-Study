from hypothesis import given, strategies as st
from decimal import Decimal, localcontext

# Summary: Generate Decimals from integers, finite floats, and bounded-precision decimals to
# cover zeros, negatives, fractional, and varied magnitudes. Verify that fma(other, third)
# equals self*other + third where the intermediate product is computed exactly (no rounding),
# by comparing fma against a high-precision reference computation rounded to the same context.
@given(st.data())
def test_decimal_Decimal_fma():
    decimal_strategy = st.one_of(
        st.integers(min_value=-10**12, max_value=10**12).map(Decimal),
        st.floats(allow_nan=False, allow_infinity=False, width=32).map(
            lambda f: Decimal(str(f))
        ),
        st.decimals(allow_nan=False, allow_infinity=False, places=6),
    )

    @given(self_val=decimal_strategy, other=decimal_strategy, third=decimal_strategy)
    def inner(self_val, other, third):
        # Compute fma under the default context
        result = self_val.fma(other, third)

        # Reference: compute the product exactly (high precision) then add third.
        with localcontext() as ctx:
            ctx.prec = 200  # large enough to keep the product exact for our inputs
            exact_product = self_val * other
            reference = exact_product + third

        # fma should equal self*other + third with exact intermediate product.
        assert result == reference, (
            f"fma mismatch: {self_val}.fma({other}, {third}) = {result}, "
            f"expected {reference}"
        )

    inner()
# End program