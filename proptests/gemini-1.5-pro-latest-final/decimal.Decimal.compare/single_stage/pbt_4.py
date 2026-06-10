from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generates random decimals, NaNs, zeros, and infinities for comprehensive testing
@given(st.one_of(
    st.decimals(allow_nan=False),
    st.just(Decimal('NaN')),
    st.just(Decimal(0)),
    st.just(Decimal('Infinity')),
    st.just(Decimal('-Infinity'))
))
def test_decimal_compare(a):
    b = st.one_of(
        st.decimals(allow_nan=False),
        st.just(Decimal('NaN')),
        st.just(Decimal(0)),
        st.just(Decimal('Infinity')),
        st.just(Decimal('-Infinity'))
    ).example()  # Draw a single example for b

    result = Decimal.compare(a, b)

    if a.is_nan() or b.is_nan():
        assert result.is_nan()
    elif a < b:
        assert result == Decimal('-1')
    elif a == b:
        assert result == Decimal('0')
    else:
        assert result == Decimal('1')
# End program