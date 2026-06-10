from hypothesis import given, strategies as st
from datetime import date

@given(st.integers(min_value=1, max_value=9999), st.integers(min_value=1, max_value=12), st.integers(min_value=1, max_value=31))
def test_isocalendar(year, month, day):
    # Ensure month and day are valid for the given year to prevent errors
    if month == 2 and day > 29:
        day = 28
    if month in [4, 6, 9, 11] and day > 30:
        day = 30
    
    try:
        test_date = date(year, month, day)
    except ValueError:
        # Skip testing invalid dates
        return

    iso_year, iso_week, iso_weekday = test_date.isocalendar()

    # Test property 1
    assert isinstance(iso_year, int)
    assert 1 <= iso_year <= 9999

    # Test property 2
    assert isinstance(iso_week, int)
    assert 1 <= iso_week <= 53

    # Test property 3
    assert isinstance(iso_weekday, int)
    assert 1 <= iso_weekday <= 7

    # Test property 4
    assert test_date == date(year, month, day)

    # Test property 5
    assert abs(iso_year - test_date.year) <= 1
# End program