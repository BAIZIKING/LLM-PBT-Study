from hypothesis import given, strategies as st
from datetime import datetime, date

@given(st.integers(min_value=1, max_value=9999), st.integers(min_value=1, max_value=12), st.integers(min_value=1, max_value=31))
def test_isocalendar_properties(year, month, day):
    try:
        dt = date(year, month, day)
        result = dt.isocalendar()
    except ValueError: # This will happen when the day is invalid for the given month/year, and we can ignore it
        return

    assert isinstance(result, type(date(1, 1, 1).isocalendar()))
    assert isinstance(result[0], int) and result[0] > 0
    assert isinstance(result[1], int) and 1 <= result[1] <= 53
    assert isinstance(result[2], int) and 1 <= result[1] <= 7

def test_sanity_check():
    assert date(2004, 1, 4).isocalendar() == (2004, 1, 7)
# End program