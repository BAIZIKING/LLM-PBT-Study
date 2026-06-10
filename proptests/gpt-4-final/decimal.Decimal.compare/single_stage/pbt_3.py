from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation

# To generate the strategies, we will implement decimals() and none()
# To generate both valid and edge cases (i.e., NaN and None)
@given(st.one_of(st.none(), st.decimals(allow_nan=True)))
def test_decimal_compare(data):
    try:
        result = Decimal(1).compare(data)  # compare to 1
        # check the properties
        assert result in (Decimal('-1'), Decimal('0'), Decimal('1')) or result.is_nan()
    except InvalidOperation:  # None input will cause an exception
        assert data is None

# End program