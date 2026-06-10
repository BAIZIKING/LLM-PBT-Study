from hypothesis import given, strategies as st
from decimal import Decimal, localcontext

# Summary: Build Decimals from bounded integers, finite floats, and numeric
# strings (no NaN/Inf, modest magnitude/precision). The documented contract is
# that fma computes self*other+third WITHOUT rounding the intermediate product.
# In a very-high-precision context the product self*other is exact, so
# fma(other, third) must equal (self*other)+third evaluated in that same
# context. We assert this equality, plus the documented example.
@given(st.data())
def test_decimal_Decimal_fma(data):
    decimals = st.one_of(
        st.integers(min_value=-10**12, max_value=10**12).map(Decimal),
        st.floats(allow_nan=False, allow_infinity=False,
                  min_value=-1e6, max_value=1e6).map(lambda f: Decimal(str(f))),
        st.from_regex(r"-?[0-9]{1,8}(\.[0-9]{1,8})?", fullmatch=True).map(Decimal),
    )

    a = data.draw(decimals)
    b = data.draw(decimals)
    c = data.draw(decimals)

    # Documented example.
    assert Decimal(2).fma(3, 5) == Decimal('11')

    with localcontext() as ctx:
        ctx.prec = 200  # high precision so a*b is exact and the add isn't lost
        fma_result = a.fma(b, c, context=ctx)
        plain_result = (a * b) + c

    assert fma_result == plain_result
# End program