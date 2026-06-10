from hypothesis import given, strategies as st
from datetime import date

# Summary: Generates diverse dates across years, months, and days, including edge cases.
@given(year=st.integers(min_value=1, max_value=9999),
       month=st.integers(min_value=1, max_value=12),
       day=st.integers(min_value=1, max_value=31))
def test_datetime_date_isocalendar(year, month, day):
    try:
        d = date(year, month, day)
    except ValueError:
        # Ignore invalid dates (e.g., February 30th)
        return

    iso_date = d.isocalendar()

    # Check return type and components
    assert isinstance(iso_date, date.IsoCalendarDate)
    assert hasattr(iso_date, 'year')
    assert hasattr(iso_date, 'week')
    assert hasattr(iso_date, 'weekday')

    # Validate week range
    assert 1 <= iso_date.week <= 53

    # Validate weekday range
    assert 1 <= iso_date.weekday <= 7

    # Check first week logic for dates near year boundary
    if month == 12 and 29 <= day <= 31:
        assert iso_date.year == year + 1
        assert iso_date.week == 1
    elif month == 1 and day <= 3:
        assert iso_date.year == year - 1
        assert iso_date.week >= 52

# End program