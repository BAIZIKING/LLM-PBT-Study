from hypothesis import given, strategies as st
from decimal import Decimal, Context

# Summary: Generate two Decimal instances across ordinary finite values plus edge cases such as NaN, infinities, signed zeros, tiny/huge exponents, and optional Context objects; check that compare() returns NaN if either operand is NaN, otherwise -1/0/1 matching numeric ordering.
@given(st.data())
def test_decimal_Decimal_compare(data):
    edge_decimals = st.sampled_from([
        Decimal("NaN"),
        Decimal("-NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
        Decimal("0"),
        Decimal("-0"),
        Decimal("0E+100"),
        Decimal("-0E-100"),
        Decimal("1"),
        Decimal("-1"),
        Decimal("1E-1000000"),
        Decimal("-1E-1000000"),
        Decimal("1E+1000000"),
        Decimal("-1E+1000000"),
        Decimal("9999999999999999999999999999"),
        Decimal("-9999999999999999999999999999"),
    ])

    finite_decimals = st.decimals(
        allow_nan=False,
        allow_infinity=False,
        places=None,
    )

    decimal_values = st.one_of(finite_decimals, edge_decimals)

    contexts = st.one_of(
        st.none(),
        st.builds(
            Context,
            prec=st.integers(min_value=1, max_value=50),
            Emin=st.integers(min_value=-1000, max_value=0),
            Emax=st.integers(min_value=0, max_value=1000),
        ),
    )

    a = data.draw(decimal_values, label="a")
    other = data.draw(decimal_values, label="other")
    context = data.draw(contexts, label="context")

    result = a.compare(other) if context is None else a.compare(other, context=context)

    assert isinstance(result, Decimal)

    if a.is_nan() or other.is_nan():
        assert result.is_nan()
    elif a < other:
        assert result == Decimal("-1")
    elif a == other:
        assert result == Decimal("0")
    else:
        assert a > other
        assert result == Decimal("1")
# End program