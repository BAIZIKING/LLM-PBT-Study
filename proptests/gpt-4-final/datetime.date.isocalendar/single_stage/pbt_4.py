from hypothesis import given, strategies as st
from datetime import date

@given(st.dates(min_value=date(1582,1,1), max_value=date(4000,12,31)))
def test_date_isocalendar(input_date):
    # Use the isocalendar method on the input date
    iso_date = input_date.isocalendar()

    # Check that the year is within one of the original date's year
    assert input_date.year - 1 <= iso_date.year <= input_date.year + 1

    # Check that the week is a valid ISO week 
    # (1-53, as some years have 53 weeks)
    assert 1 <= iso_date.week <= 53

    # Check that the weekday is a valid ISO weekday (1 [Monday] - 7 [Sunday])
    assert 1 <= iso_date.weekday <= 7
# End program