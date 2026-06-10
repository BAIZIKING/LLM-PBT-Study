from hypothesis import given, strategies as st
from math import gcd
import decimal
from decimal import Decimal


# Strategy for finite Decimals (avoiding infinities and NaNs)
finite_decimals = st.decimals(allow_nan=False, allow_infinity=False)

# Strategy for non-finite Decimals (infinities and NaNs)
nonfinite_decimals = st.sampled_from([
    Decimal('Infinity'),
    Decimal('-Infinity'),
    Decimal('NaN'),
    Decimal('-NaN'),
    Decimal('sNaN'),
])


@given(st.data())
def test_decimal_Decimal_as_integer_ratio_property():
    # Use a large enough context to avoid spurious errors on big exponents
    with decimal.localcontext() as ctx:
        ctx.prec = 100
        ctx.Emax = 999999999
        ctx.Emin = -999999999

        # ---- Property 1: denominator is always a positive integer ----
        d_val = data_draw_finite()
        # (placeholder to keep structure; real draws happen below)

    # Property 1: denominator positive
    @given(finite_decimals)
    def _prop_positive_denominator(value):
        with decimal.localcontext() as ctx:
            ctx.prec = 100
            ctx.Emax = 999999999
            ctx.Emin = -999999999
            n, den = value.as_integer_ratio()
            assert isinstance(den, int)
            assert den > 0

    # Property 2: fraction is in lowest terms (gcd == 1)
    @given(finite_decimals)
    def _prop_lowest_terms(value):
        with decimal.localcontext() as ctx:
            ctx.prec = 100
            ctx.Emax = 999999999
            ctx.Emin = -999999999
            n, den = value.as_integer_ratio()
            assert gcd(abs(n), den) == 1

    # Property 3: ratio is exact reconstruction
    @given(finite_decimals)
    def _prop_exact(value):
        with decimal.localcontext() as ctx:
            ctx.prec = 100
            ctx.Emax = 999999999
            ctx.Emin = -999999999
            n, den = value.as_integer_ratio()
            # Reconstruct exactly using Fraction-style comparison:
            # value == n / den  =>  value * den == n
            assert value * Decimal(den) == Decimal(n)

    # Property 4: sign of numerator matches sign of value
    @given(finite_decimals)
    def _prop_sign(value):
        with decimal.localcontext() as ctx:
            ctx.prec = 100
            ctx.Emax = 999999999
            ctx.Emin = -999999999
            n, den = value.as_integer_ratio()
            if value > 0:
                assert n > 0
            elif value < 0:
                assert n < 0
            else:
                assert n == 0

    # Property 5: infinities raise OverflowError, NaNs raise ValueError
    @given(nonfinite_decimals)
    def _prop_nonfinite(value):
        if value.is_nan():
            try:
                value.as_integer_ratio()
                assert False, "Expected ValueError for NaN"
            except ValueError:
                pass
        elif value.is_infinite():
            try:
                value.as_integer_ratio()
                assert False, "Expected OverflowError for infinity"
            except OverflowError:
                pass

    # Run each sub-property
    _prop_positive_denominator()
    _prop_lowest_terms()
    _prop_exact()
    _prop_sign()
    _prop_nonfinite()


def data_draw_finite():
    # Helper placeholder (not used in actual assertions)
    return Decimal('0')
# End program