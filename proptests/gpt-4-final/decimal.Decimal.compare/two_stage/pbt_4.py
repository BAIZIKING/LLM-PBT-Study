from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation

@given(st.decimals(allow_nan=True, allow_infinity=True), st.decimals(allow_nan=True, allow_infinity=True))
def test_decimal_compare_property(a, b):
    try:
        result = a.compare(b)
    except InvalidOperation:
        assert a.is_nan() or b.is_nan()
    else:
        if a == b:
            assert result == Decimal('0')
        elif a < b:
            assert result == Decimal('-1')
        elif a > b:
            assert result == Decimal('1')

        assert isinstance(result, Decimal)
        assert str(result) in ['NaN', '-1', '0', '1']
# End program