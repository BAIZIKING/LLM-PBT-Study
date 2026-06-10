from hypothesis import given, strategies as st
import decimal

finite_decimals = st.decimals(
    min_value=decimal.Decimal("-1e100"),
    max_value=decimal.Decimal("1e100"),
    places=20,
    allow_nan=False,
    allow_infinity=False,
)

decimal_values = st.one_of(
    finite_decimals,
    st.sampled_from(
        [
            decimal.Decimal("NaN"),
            decimal.Decimal("Infinity"),
            decimal.Decimal("-Infinity"),
        ]
    ),
)


@given(st.data())
def test_decimal_Decimal_compare_property(data):
    a = data.draw(decimal_values)
    b = data.draw(decimal_values)

    result = a.compare(b)

    if a.is_nan() or b.is_nan():
        assert result.is_nan()
    else:
        assert result in {
            decimal.Decimal("-1"),
            decimal.Decimal("0"),
            decimal.Decimal("1"),
        }

        if a < b:
            assert result == decimal.Decimal("-1")

        if a == b:
            assert result == decimal.Decimal("0")

        if a > b:
            assert result == decimal.Decimal("1")

        swapped_result = b.compare(a)
        assert result == -swapped_result
# End program