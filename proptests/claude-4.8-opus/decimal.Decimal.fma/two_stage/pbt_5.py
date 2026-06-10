from hypothesis import given, strategies as st
import decimal
from decimal import Decimal, localcontext

# Strategy for generating "reasonable" Decimal values to avoid overflow issues.
# We limit the magnitude and precision to keep intermediate products in range.
def decimal_strategy():
    return st.one_of(
        st.integers(min_value=-10**6, max_value=10**6).map(Decimal),
        st.floats(
            min_value=-1e6,
            max_value=1e6,
            allow_nan=False,
            allow_infinity=False,
        ).map(lambda f: Decimal(repr(f))),
    )


# Property 1:
# For exact-arithmetic cases (using a high-precision context), the result of
# self.fma(other, third) equals self*other + third computed directly.
@given(st.data())
def test_decimal_Decimal_fma_exact_matches_direct(data):
    self = data.draw(decimal_strategy())
    other = data.draw(decimal_strategy())
    third = data.draw(decimal_strategy())
    # Use a large precision so no rounding occurs in either computation.
    with localcontext() as ctx:
        ctx.prec = 100
        result = self.fma(other, third)
        direct = self * other + third
        assert result == direct
# End program


# Property 2:
# fma avoids rounding the intermediate product, whereas (self*other)+third may
# round it. We check that fma equals the result computed when the intermediate
# product is done at high precision and only the final add uses normal precision.
@given(st.data())
def test_decimal_Decimal_fma_no_intermediate_rounding(data):
    self = data.draw(decimal_strategy())
    other = data.draw(decimal_strategy())
    third = data.draw(decimal_strategy())
    prec = data.draw(st.integers(min_value=2, max_value=30))

    with localcontext() as ctx:
        ctx.prec = prec
        fma_result = self.fma(other, third)

    # Compute the unrounded product at very high precision.
    with localcontext() as hp:
        hp.prec = 200
        exact_product = self * other

    # Now add 'third' to the exact product at the normal precision.
    with localcontext() as ctx:
        ctx.prec = prec
        emulated = exact_product + third

    assert fma_result == emulated
# End program


# Property 3:
# When third is zero, self.fma(other, 0) equals the product self*other
# (subject only to final rounding from addition, which for adding zero is none).
@given(st.data())
def test_decimal_Decimal_fma_third_zero(data):
    self = data.draw(decimal_strategy())
    other = data.draw(decimal_strategy())

    with localcontext() as ctx:
        ctx.prec = 50
        result = self.fma(other, Decimal(0))
        product = self * other
        assert result == product
# End program


# Property 4:
# When other is one, self.fma(1, third) equals self + third.
@given(st.data())
def test_decimal_Decimal_fma_other_one(data):
    self = data.draw(decimal_strategy())
    third = data.draw(decimal_strategy())

    with localcontext() as ctx:
        ctx.prec = 50
        result = self.fma(Decimal(1), third)
        expected = self + third
        assert result == expected
# End program


# Property 5:
# fma is commutative in its first two arguments:
# self.fma(other, third) == other.fma(self, third).
@given(st.data())
def test_decimal_Decimal_fma_commutative(data):
    self = data.draw(decimal_strategy())
    other = data.draw(decimal_strategy())
    third = data.draw(decimal_strategy())

    with localcontext() as ctx:
        ctx.prec = 50
        result1 = self.fma(other, third)
        result2 = other.fma(self, third)
        assert result1 == result2
# End program