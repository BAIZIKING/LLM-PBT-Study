from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation

@given(a=st.decimals(allow_nan=True, allow_infinity=True), b=st.decimals(allow_nan=True,  allow_infinity=True))
def test_decimal_compare(a, b):
    try:
        res = Decimal.compare(a, b)
    except InvalidOperation:
        # If either a or b is a NaN, a InvalidOperation is raised. 
        assert a.is_nan() or b.is_nan()
        return
    if a < b:
        assert res == Decimal('-1')
    elif a == b:
        assert res == Decimal('0')
    else:
        assert res == Decimal('1')