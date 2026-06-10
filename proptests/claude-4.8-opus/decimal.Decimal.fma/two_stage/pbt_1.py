from hypothesis import given, strategies as st, settings, assume
import decimal
from decimal import Decimal

# Strategy for generating "reasonable" Decimal values that avoid overflow.
# We bound the exponent and the number of digits to keep products manageable.
decimal_strategy = st.one_of(
    st.integers(min_value=-10**6, max_value=10**6).map(Decimal),
    st.fractions(
        min_value=-10**6, max_value=10**6, max_denominator=10**6
    ).map(lambda f: Decimal(f.numerator) / Decimal(f.denominator)),
    st.decimals(
        min_value=Decimal("-1e50"),
        max_value=Decimal("1e50"),
        allow_nan=False,
        allow_infinity=False,
        places=10,
    ),
)


@given(st.data())
@settings(max_examples=500)
def test_decimal_Decimal_fma_property(data):
    # Use a high-precision context to do reference computations.
    ref_ctx = decimal.Context(prec=200)

    self_val = data.draw(decimal_strategy, label="self")
    other = data.draw(decimal_strategy, label="other")
    third = data.draw(decimal_strategy, label="third")

    # ---- Property 1: fma matches self*other+third with sufficient precision ----
    # Compute reference using a context with enough precision to be exact for our
    # bounded inputs.
    result = self_val.fma(other, third, context=ref_ctx)
    expected = ref_ctx.add(ref_ctx.multiply(self_val, other), third)
    assert result == expected

    # ---- Property 2: third == 0 => fma == self*other ----
    res_zero_third = self_val.fma(other, Decimal(0), context=ref_ctx)
    expected_zero_third = ref_ctx.multiply(self_val, other)
    assert res_zero_third == expected_zero_third

    # ---- Property 3: other == 0 => fma == third ----
    res_zero_other = self_val.fma(Decimal(0), third, context=ref_ctx)
    # self*0 = 0, so result should equal third (compared numerically).
    assert res_zero_other == third

    # ---- Property 4: other == 1 => fma == self + third ----
    res_one_other = self_val.fma(Decimal(1), third, context=ref_ctx)
    expected_one_other = ref_ctx.add(self_val, third)
    assert res_one_other == expected_one_other

    # ---- Property 5: fma is at least as accurate as separate rounded computation ----
    # Use a low-precision context where rounding the intermediate product can lose
    # precision. fma avoids rounding the intermediate product, so it should be at
    # least as close to the high-precision reference as the separate computation.
    low_ctx = decimal.Context(prec=5)

    fma_low = self_val.fma(other, third, context=low_ctx)
    separate_low = low_ctx.add(low_ctx.multiply(self_val, other), third)

    # High precision reference for the true value.
    true_val = ref_ctx.add(ref_ctx.multiply(self_val, other), third)

    err_fma = abs(ref_ctx.subtract(fma_low, true_val))
    err_separate = abs(ref_ctx.subtract(separate_low, true_val))

    assert err_fma <= err_separate
# End program