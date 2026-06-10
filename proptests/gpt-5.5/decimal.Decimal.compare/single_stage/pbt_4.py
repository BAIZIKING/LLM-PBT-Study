from hypothesis import given, strategies as st

# Summary: Generate two Decimal instances from quiet NaNs, infinities, signed zeros, hand-picked boundary-like values, and arbitrary finite Decimals with varied signs, digits, and exponents. Check that compare() always returns a Decimal; if either operand is NaN the result is NaN, otherwise it returns Decimal('-1'), Decimal('0'), or Decimal('1') according to numeric ordering.
@given(st.data())
def test_decimal_Decimal_compare(data):
    from decimal import Decimal

    finite_decimals = st.builds(
        lambda sign, digits, exponent: Decimal((sign, tuple(digits), exponent)),
        sign=st.integers(min_value=0, max_value=1),
        digits=st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=50),
        exponent=st.integers(min_value=-1000, max_value=1000),
    )

    edge_decimals = st.sampled_from(
        [
            Decimal("NaN"),
            Decimal("-NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
            Decimal("0"),
            Decimal("-0"),
            Decimal("1"),
            Decimal("-1"),
            Decimal("10"),
            Decimal("-10"),
            Decimal("0.1"),
            Decimal("-0.1"),
            Decimal("1E-1000"),
            Decimal("-1E-1000"),
            Decimal("1E+1000"),
            Decimal("-1E+1000"),
        ]
    )

    decimal_values = st.one_of(edge_decimals, finite_decimals)

    a = data.draw(decimal_values, label="a")
    b = data.draw(decimal_values, label="b")

    result = a.compare(b)

    assert isinstance(result, Decimal)

    if a.is_nan() or b.is_nan():
        assert result.is_nan()
    elif a < b:
        assert result == Decimal("-1")
    elif a == b:
        assert result == Decimal("0")
    else:
        assert a > b
        assert result == Decimal("1")
# End program