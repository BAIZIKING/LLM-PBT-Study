from hypothesis import given, strategies as st

# Summary: Test decimal.Decimal.from_float using randomly generated float, integer, and special float values ('nan', 'inf', '-inf')
@given(st.one_of(
    st.floats(allow_nan=True, allow_infinity=True), 
    st.integers()
    ))
def test_decimal_from_float(value):
    from decimal import Decimal, InvalidOperation
    
    try:
        result = Decimal.from_float(value)
    except InvalidOperation:
        # Invalid input for non-numbers, nan, inf and -inf, considered a pass
        assert value != value or value in (float('inf'), float('-inf'))  # NaN != NaN
    else:
        # It's a proper number, so method should work fine
        assert isinstance(result, Decimal)
        assert float(result) == value

# End program