from hypothesis import given, strategies as st
from datetime import date

# Generate a wide variety of valid dates between year 1 and 9999. 
# Include leap years and dates that fall on first/last days of the year, month, and week,
# to test edge cases around month, year and week number boundaries.
@given(st.dates(min_value=date(1,1,1), max_value=date(9999,12,31)))
def test_date_isocalendar(d):
    iso_date = d.isocalendar()
    
    # Check that iso_date is a named tuple with 3 integer components
    assert isinstance(iso_date, tuple)
    assert len(iso_date) == 3
    assert all(isinstance(x, int) for x in iso_date)
    
    iso_year, iso_week, iso_weekday = iso_date
    
    # Check that ISO year matches Gregorian year of given date's Thursday  
    thu_date = d + timedelta(days=3-d.isoweekday()) 
    assert iso_year == thu_date.year
    
    # Check that week number is in range 1-53
    assert 1 <= iso_week <= 53
    
    # Check that weekday is in range 1-7  
    assert 1 <= iso_weekday <= 7
    
# End program