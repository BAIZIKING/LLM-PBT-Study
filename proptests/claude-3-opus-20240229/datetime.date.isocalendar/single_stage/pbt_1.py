from hypothesis import given, strategies as st
from datetime import date, timedelta

# Generate a wide variety of valid dates, focusing on edge cases around 
# the start/end of years and weeks. Generate mostly dates in the 
# 21st century but include some earlier and later dates as well.
@given(st.dates(min_value=date(1900,1,1), max_value=date(2100,12,31)))  
def test_date_isocalendar(d):
    iso_date = d.isocalendar()
    assert isinstance(iso_date, tuple)
    assert len(iso_date) == 3
    iso_year, iso_week, iso_weekday = iso_date

    # Check ISO year 
    assert isinstance(iso_year, int)
    assert 1900 <= iso_year <= 2100

    # Check ISO week
    assert isinstance(iso_week, int)
    assert 1 <= iso_week <= 53

    # Check ISO weekday 
    assert isinstance(iso_weekday, int)
    assert 1 <= iso_weekday <= 7

    # Check that roundtrip conversion from iso back to date works
    assert date.fromisocalendar(*iso_date) == d

    # Check that incrementing the date by a week increments the ISO week
    next_week_date = d + timedelta(days=7) 
    next_week_iso = next_week_date.isocalendar()
    assert (iso_week + 1) % 53 == next_week_iso[1] % 53
# End program