from hypothesis import given, strategies as st
from datetime import date

# Summary: Generate diverse dates and check properties of isocalendar result
@given(year=st.integers(min_value=-9999, max_value=9999), 
       month=st.integers(min_value=1, max_value=12),
       day=st.integers(min_value=1, max_value=31),
       date_near_iso_year_boundary=st.booleans())
def test_datetime_date_isocalendar(year, month, day, date_near_iso_year_boundary):
    # Adjust day based on month and year to avoid invalid dates
    day = min(day, calendar.monthrange(year, month)[1]) 
    
    # Generate dates near ISO year boundaries
    if date_near_iso_year_boundary:
        month = 12 if st.random().random() < 0.5 else 1
        day = st.integers(min_value=28, max_value=31).example()

    test_date = date(year, month, day)
    result = test_date.isocalendar()

    # Check data type and components
    assert isinstance(result, date.IsoCalendarDate)
    assert hasattr(result, 'year')
    assert hasattr(result, 'week')
    assert hasattr(result, 'weekday')

    # Check year value based on ISO year definition
    iso_year_start = date(year, 1, 1).isocalendar().week > 50 and date(year, 12, 31).isocalendar().week == 1
    expected_year = year + 1 if iso_year_start else year
    assert result.year == expected_year

    # Check week and weekday ranges
    assert 1 <= result.week <= 53
    assert 1 <= result.weekday <= 7

    # Check consistency for dates in the same ISO week
    next_day = test_date + timedelta(days=1)
    next_day_result = next_day.isocalendar()
    if result.week == next_day_result.week:
        assert result.year == next_day_result.year

# End program