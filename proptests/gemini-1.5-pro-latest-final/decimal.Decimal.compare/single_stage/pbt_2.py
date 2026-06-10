from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generate diverse decimal values, including NaN and edge cases, to test comparison behavior.
@given(st.data())
def test_decimal_compare(data):
    # Generate decimal values, including NaN and edge cases.
    a = data.draw(st.one_of(
        st.decimals(allow_nan=True),
        st.just(Decimal('NaN')),
        st.decimals(min_value=-Decimal('Infinity'), max_value=Decimal('Infinity'), allow_nan=False)
    ))
    b = data.draw(st.decimals(allow_nan=True))

    result = Decimal.compare(a, b)

    # Check for NaN comparison results.
    if a.is_nan() or b.is_nan():
        assert result.is_nan()
    else:
        # Check for correct comparison results.
        if a < b:
            assert result == Decimal('-1')
        elif a == b:
            assert result == Decimal('0')
        else:
            assert result == Decimal('1')

# End program