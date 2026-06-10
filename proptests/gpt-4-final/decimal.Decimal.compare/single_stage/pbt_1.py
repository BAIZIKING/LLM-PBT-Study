from hypothesis import given, assume, strategies as st
from decimal import Decimal, InvalidOperation

def compare_decimals(a, b):
    try:
        result = a.compare(b)
        return result
    except InvalidOperation:
        return Decimal('NaN')

@given(st.data())
def test_decimal_compare(data):
    # we use data() rather than floats() so we can draw NaNs
    a = data.draw(st.floats(allow_nan=True, allow_infinity=True))
    b = data.draw(st.floats(allow_nan=True, allow_infinity=True))

    result = compare_decimals(Decimal(a), Decimal(b))

    # handle NaNs
    if a!=a or b!=b: # This is the way to check if a or b is NaN as NaN != NaN
        assert result!=result # The result should be NaN
    else:
        # check the result of the compare function
        assert (a < b and result == Decimal('-1')) or (
            a == b and result == Decimal('0')) or (
            a > b and result == Decimal('1'))