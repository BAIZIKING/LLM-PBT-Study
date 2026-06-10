from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generates diverse Decimal inputs, including normal values, edge cases, and special values.
@given(st.data())
def test_decimal_compare(data):
    # Generate diverse Decimal inputs
    d1 = data.draw(st.one_of(
        st.decimals(min_value=-1e10, max_value=1e10, allow_nan=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.sampled_from([Decimal('NaN'), Decimal('Infinity'), Decimal('-Infinity')]),
        st.none()
    ))
    d2 = data.draw(st.one_of(
        st.decimals(min_value=-1e10, max_value=1e10, allow_nan=False),
        st.floats(allow_nan=False, allow_infinity=False),
        st.sampled_from([Decimal('NaN'), Decimal('Infinity'), Decimal('-Infinity')]),
        st.none()
    ))

    # Check for NaN comparison
    if d1 is None or d2 is None or d1.is_nan() or d2.is_nan():
        assert Decimal.compare(d1, d2) == Decimal('NaN')
    else:
        # Check order comparison
        if d1 < d2:
            assert Decimal.compare(d1, d2) == Decimal('-1')
        elif d1 == d2:
            assert Decimal.compare(d1, d2) == Decimal('0')
        else:
            assert Decimal.compare(d1, d2) == Decimal('1')
# End program