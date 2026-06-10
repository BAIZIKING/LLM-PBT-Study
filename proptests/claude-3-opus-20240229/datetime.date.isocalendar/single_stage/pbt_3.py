from hypothesis import given, strategies as st
from datetime import date

# Summary: Generate random valid date values covering a wide range. Check that
# the isocalendar() result matches expected properties from the documentation.
@given(st.dates(min_value=date(1, 1, 1), max_value=date(9999, 12, 31)))
def test_datetime_date_isocalendar(dt):
    iso_date = dt.isocalendar()
    iso_year, iso_week, iso_weekday = iso_date
    
    # Check year is in valid range 
    assert 1 <= iso_year <= 9999
    
    # Check week is in valid range
    assert 1 <= iso_week <= 53
    
    # Check weekday is in valid range (1=Monday to 7=Sunday)
    assert 1 <= iso_weekday <= 7
    
    # Check that the ISO year matches the Gregorian year for dates 
    # in week 1 containing a Thursday 
    if iso_week == 1 and iso_weekday >= 4:
        assert iso_year == dt.year
    elif iso_week >= 52 and iso_weekday < 4: 
        assert iso_year == dt.year + 1
    else:
        assert iso_year == dt.year
        
# End program        