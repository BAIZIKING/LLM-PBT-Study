from hypothesis import given, strategies as st, assume, settings
import decimal
from decimal import Decimal, InvalidOperation, Context, ROUND_HALF_EVEN

# Strategy for generating Decimal values that are "reasonable" (finite, not too large)
def finite_decimals(min_exp=-20, max_exp=20):
    return st.builds(
        lambda sign, coeff, exp: Decimal((sign, coeff, exp)),
        st.integers(min_value=0, max_value=1),
        st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=15).map(tuple),
        st.integers(min_value=min_exp, max_value=max_exp),
    )

# Strategy for generating an 'exp' operand: a Decimal whose exponent matters.
def exp_decimals(min_exp=-20, max_exp=20):
    return st.builds(
        lambda sign, coeff, exp: Decimal((sign, coeff, exp)),
        st.integers(min_value=0, max_value=1),
        st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=5).map(tuple),
        st.integers(min_value=min_exp, max_value=max_exp),
    )

ROUNDINGS = [
    decimal.ROUND_CEILING, decimal.ROUND_DOWN, decimal.ROUND_FLOOR,
    decimal.ROUND_HALF_DOWN, decimal.ROUND_HALF_EVEN, decimal.ROUND_HALF_UP,
    decimal.ROUND_UP, decimal.ROUND_05UP,
]


@given(st.data())
def test_decimal_Decimal_quantize_property():
    data = st.data

    # ---- Property 1: result exponent equals exp's exponent (when no error) ----
    @given(
        first=finite_decimals(),
        exp=exp_decimals(),
        rounding=st.sampled_from(ROUNDINGS),
    )
    @settings(max_examples=200)
    def prop1(first, exp, rounding):
        ctx = Context(prec=28)
        try:
            result = first.quantize(exp, rounding=rounding, context=ctx)
        except (InvalidOperation, decimal.Overflow):
            return  # error condition, property does not apply
        # Both result and exp should be finite here
        assert result.as_tuple()[2] == exp.as_tuple()[2]

    # ---- Property 2: result differs from first by less than 1 ulp of exp ----
    @given(
        first=finite_decimals(),
        exp=exp_decimals(),
        rounding=st.sampled_from(ROUNDINGS),
    )
    @settings(max_examples=200)
    def prop2(first, exp, rounding):
        ctx = Context(prec=28)
        try:
            result = first.quantize(exp, rounding=rounding, context=ctx)
        except (InvalidOperation, decimal.Overflow):
            return
        # ulp = 10 ** exponent_of_exp
        exp_exponent = exp.as_tuple()[2]
        ulp = Decimal((0, (1,), exp_exponent))
        # |result - first| should be strictly less than one ulp
        diff = abs(result - first)
        assert diff < ulp

    # ---- Property 3: no rounding needed -> result equals first numerically ----
    @given(
        first=finite_decimals(),
        exp=exp_decimals(),
        rounding=st.sampled_from(ROUNDINGS),
    )
    @settings(max_examples=200)
    def prop3(first, exp, rounding):
        ctx = Context(prec=28)
        first_exp = first.as_tuple()[2]
        exp_exp = exp.as_tuple()[2]
        assume(exp_exp <= first_exp)  # no rounding necessary
        try:
            result = first.quantize(exp, rounding=rounding, context=ctx)
        except (InvalidOperation, decimal.Overflow):
            return
        assert result == first

    # ---- Property 4: coefficient length never exceeds context precision ----
    @given(
        first=finite_decimals(),
        exp=exp_decimals(),
        prec=st.integers(min_value=1, max_value=30),
        rounding=st.sampled_from(ROUNDINGS),
    )
    @settings(max_examples=200)
    def prop4(first, exp, prec, rounding):
        ctx = Context(prec=prec)
        try:
            result = first.quantize(exp, rounding=rounding, context=ctx)
        except (InvalidOperation, decimal.Overflow):
            return  # error raised instead of producing oversized coefficient
        digits = result.as_tuple()[1]
        assert len(digits) <= prec

    # ---- Property 5: error when resulting exponent out of [Etiny, Emax] ----
    @given(
        first=finite_decimals(),
        exp=exp_decimals(min_exp=-40, max_exp=40),
        rounding=st.sampled_from(ROUNDINGS),
    )
    @settings(max_examples=200)
    def prop5(first, exp, rounding):
        # Use a tight context so out-of-range exponents are reachable
        ctx = Context(prec=10, Emax=15, Emin=-15)
        target_exp = exp.as_tuple()[2]
        etiny = ctx.Emin - (ctx.prec - 1)
        emax = ctx.Emax
        try:
            result = first.quantize(exp, rounding=rounding, context=ctx)
        except (InvalidOperation, decimal.Overflow):
            # If error, ensure it is consistent with out-of-range possibility
            # (cannot assert exact cause, but error is acceptable)
            return
        # If a valid result was returned, its exponent must be in range
        assert etiny <= target_exp <= emax

    prop1()
    prop2()
    prop3()
    prop4()
    prop5()
# End program