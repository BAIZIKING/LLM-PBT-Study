from hypothesis import given, strategies as st
from decimal import Decimal, localcontext, InvalidOperation, Overflow

# Summary: Generate three Decimal values (finite values with varied magnitude/sign,
# plus signed infinities, excluding NaN to keep equality meaningful). Verify that
# fma(other, third) == self*other + third computed at very high precision (so the
# intermediate product is unrounded). Handle InvalidOperation/Overflow consistently.
@given(st.data())
def test_decimal_Decimal_fma(data):
    decimal_strategy = st.one_of(
        st.decimals(allow_nan=False, allow_infinity=True),
        st.integers(min_value=-10**6, max_value=10**6).map(Decimal),
        st.sampled_from([
            Decimal(0), Decimal("-0"),
            Decimal("Infinity"), Decimal("-Infinity"),
            Decimal("1E+10"), Decimal("1E-10"),
        ]),
    )

    self_val = data.draw(decimal_strategy, label="self")
    other = data.draw(decimal_strategy, label="other")
    third = data.draw(decimal_strategy, label="third")

    # Compute fma; capture any exception.
    fma_exc = None
    try:
        fma_result = self_val.fma(other, third)
    except (InvalidOperation, Overflow) as e:
        fma_exc = type(e)

    # Compute reference: self*other (unrounded) + third using very high precision.
    ref_exc = None
    try:
        with localcontext() as ctx:
            ctx.prec = 100000  # large enough so the intermediate product is unrounded
            ref_result = self_val * other + third
    except (InvalidOperation, Overflow) as e:
        ref_exc = type(e)

    # If either raised, both should raise the same category of exception.
    if fma_exc is not None or ref_exc is not None:
        assert fma_exc == ref_exc, (
            f"Exception mismatch: fma={fma_exc}, ref={ref_exc}"
        )
        return

    # Otherwise results must be exactly equal (no intermediate rounding in fma).
    # Use compare to handle signed zero / infinities; Decimal '==' treats 0 == -0 True.
    assert fma_result == ref_result, (
        f"fma({self_val!r}, {other!r}, {third!r}) = {fma_result!r}, "
        f"expected {ref_result!r}"
    )
# End program