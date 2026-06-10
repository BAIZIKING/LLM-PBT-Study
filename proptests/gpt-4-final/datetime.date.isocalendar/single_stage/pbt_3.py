from hypothesis import given, strategies as st
from datetime import date

@given(year=st.integers(min_value=1, max_value=9999), month=st.integers(min_value=1, max_value=12),
       day=st.integers(min_value=1, max_value=31))
def test_datetime_date_isocalendar(year, month, day):
    
    try:
        # Create date object
        d = date(year, month, day)
    except ValueError:
        # Handles invalid dates cases
        return None
    
    # Apply method isocalendar
    iso_calendar_date = d.isocalendar()
    
    # Check returned types and value range
    assert isinstance(iso_calendar_date.year, int)
    assert iso_calendar_date.year >= 1 and iso_calendar_date.year <= 9999
    assert isinstance(iso_calendar_date.week, int)
    assert iso_calendar_date.week >= 1 and iso_calendar_date.week <= 53
    assert isinstance(iso_calendar_date.weekday, int)
    assert iso_calendar_date.weekday >= 1 and iso_calendar_date.weekday <= 7

    # Check first week condition
    if iso_calendar_date.week == 1 and d.month == 1 and d.day <= 4:
        assert d.weekday() in [3, 4, 5, 6, 7]   # the day is Thursday, Friday, Saturday, Sunday or Monday
# End program