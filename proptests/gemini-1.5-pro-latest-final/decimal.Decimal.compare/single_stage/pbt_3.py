from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generates random Decimal instances, including NaNs and edge cases.
@given(st.data())
def test_decimal_compare(data):
    # Generate random Decimal instances with varying precision and scale.
    a = data.draw(st.decimals(
        min_value=-1e100, max_value=1e100, allow_nan=True, allow_infinity=False
    ))
    b = data.draw(st.decimals(
        min_value=-1e100, max_value=1e100, allow_nan=True, allow_infinity=False
    ))

    result = Decimal.compare(a, b)

    # Check for NaN handling
    if a.is_nan() or b.is_nan():
        assert result.is_nan()
    else:
        # Check comparison results
        if a < b:
            assert result == Decimal('-1')
        elif a == b:
            assert result == Decimal('0')
        else:
            assert result == Decimal('1')
# End program