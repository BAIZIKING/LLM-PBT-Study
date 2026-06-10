from hypothesis import given, strategies as st
from datetime import date, timedelta

# Generate random dates between date.min and date.max.
# Include some edge cases like date.min, date.max, 
# and dates around the new year transition.
@given(st.dates(min_value=date.min, max_value=date.max) | st.just(date.min) | st.just(date.max) |
       st.dates(min_value=date(2022,12,20), max_value=date(2023,1,10)))
def test_date_isocalendar(dt):
    iso_date = dt.isocalendar()
    iso_year, iso_week, iso_weekday = iso_date
    
    # Check that iso_year matches dt.year, except it may be 1 less 
    # for a few days at the beginning of January 
    assert iso_year == dt.year or (dt.month == 1 and iso_year == dt.year - 1)
    
    # Check that iso_week is in range [1, 53]
    assert 1 <= iso_week <= 53
    
    # Check that iso_weekday is in range [1, 7]
    assert 1 <= iso_weekday <= 7
    
    # Check that we can go from iso date back to original date
    iso_to_greg_dt = date.fromisocalendar(iso_year, iso_week, iso_weekday)
    assert iso_to_greg_dt == dt
    
# End program