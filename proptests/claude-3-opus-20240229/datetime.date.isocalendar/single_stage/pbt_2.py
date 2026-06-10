from hypothesis import given, strategies as st
from datetime import date

# Generate a wide variety of valid date inputs, including edge cases like
# Jan 1, Dec 31, Feb 29 on leap years, dates in the far past/future.
# Use built-in hypothesis date strategy.
@given(st.dates())
def test_date_isocalendar(d):
    iso_date = d.isocalendar()
    
    # Check year matches date's year
    assert iso_date.year == d.year
    
    # Check week is between 1 and 53
    assert 1 <= iso_date.week <= 53
    
    # Check weekday is between 1 (Monday) and 7 (Sunday)
    assert 1 <= iso_date.weekday <= 7

    # Check that Jan 4 is always in week 1
    jan_4_date = date(d.year, 1, 4)
    jan_4_iso = jan_4_date.isocalendar() 
    assert jan_4_iso.week == 1

    # Check Dec 28 is in last week of year if not a Monday
    dec_28_date = date(d.year, 12, 28)
    dec_28_iso = dec_28_date.isocalendar()
    if dec_28_date.isoweekday() != 1:
        assert dec_28_iso.week == 52 or dec_28_iso.week == 53
# End program        