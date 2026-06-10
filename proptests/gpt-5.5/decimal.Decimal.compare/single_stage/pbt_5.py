from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generate both Decimal operands from a mix of arbitrary Decimal values and explicit edge cases: quiet NaNs, signed zeros, infinities, small integers, fractions, and very large/small exponents. Exclude signaling NaNs because their behavior can depend on context traps, while this API documentation specifies quiet NaN-style comparison results.
@given(st.data())
def test_decimal_Decimal_compare(data):
    decimal_values = st.one_of(
        st.decimals(
            allow_nan=True,
            allow_infinity=True,
            places=None,
        ).filter(lambda d: not d.is_snan()),
        st.sampled_from(
            [
                Decimal("NaN"),
                Decimal("-NaN"),
                Decimal("0"),
                Decimal("-0"),
                Decimal("1"),
                Decimal("-1"),
                Decimal("0.1"),
                Decimal("-0.1"),
                Decimal("Infinity"),
                Decimal("-Infinity"),
                Decimal("1E+999999"),
                Decimal("-1E+999999"),
                Decimal("1E-999999"),
                Decimal("-1E-999999"),
            ]
        ),
    )

    a = data.draw(decimal_values)
    other = data.draw(decimal_values)

    result = a.compare(other)

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