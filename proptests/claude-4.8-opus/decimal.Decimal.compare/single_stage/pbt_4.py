from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generate two Decimal values using st.decimals(), enabling NaN and
# infinity to cover special-value edge cases as well as regular numbers, zeros,
# negatives, and varied fractional/large values. Verify the return type, NaN
# propagation, and correct -1/0/1 comparison results per the documentation.
@given(st.data())
def test_decimal_Decimal_compare(data):
    decimal_strategy = st.decimals(allow_nan=True, allow_infinity=True)
    a = data.draw(decimal_strategy, label="a")
    b = data.draw(decimal_strategy, label="b")

    result = a.compare(b)

    # Property 1: result is always a Decimal instance
    assert isinstance(result, Decimal)

    # Property 2: if either operand is NaN, result is NaN
    if a.is_nan() or b.is_nan():
        assert result.is_nan()
    else:
        # Property 4: when no NaN, result must be exactly -1, 0, or 1
        assert result in (Decimal('-1'), Decimal('0'), Decimal('1'))

        # Property 3: correct comparison results
        if a < b:
            assert result == Decimal('-1')
        elif a == b:
            assert result == Decimal('0')
        else:  # a > b
            assert result == Decimal('1')
# End program