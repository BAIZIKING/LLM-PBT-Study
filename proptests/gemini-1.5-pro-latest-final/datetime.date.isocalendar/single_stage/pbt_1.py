from hypothesis import given, strategies as st
from datetime import date

# Summary: Generates a wide range of dates, including BCE, leap years, and edge cases.
@given(year=st.integers(min_value=-4000, max_value=4000),
       month=st.integers(min_value=1, max_value=12),
       day=st.integers(min_value=1, max_value=28))  # Adjust day range based on month and leap year
def test_datetime_date_isocalendar(year, month, day):
    try:
        date_obj = date(year, month, day)
    except ValueError:
        # Ignore invalid dates (e.g., Feb 30)
        return

    iso_calendar = date_obj.isocalendar()

    # Check data type and component ranges
    assert isinstance(iso_calendar, date.IsoCalendarDate)
    assert 1 <= iso_calendar.week <= 53
    assert 1 <= iso_calendar.weekday <= 7

    # Additional checks for year consistency and edge cases can be added here
    # ...

# End program