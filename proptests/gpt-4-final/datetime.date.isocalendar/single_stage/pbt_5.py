from datetime import date
from hypothesis import given, strategies as st

@given(st.dates(min_value=date.min, max_value=date.max))
def test_date_isocalendar(d):
    iso_cal = d.isocalendar()

    # Check the returned object is a IsoCalendarDate named tuple
    assert isinstance(iso_cal, date.IsoCalendarDate)

    # Check the year value is the same as the ISO year of the date
    assert iso_cal.year == d.year

    # Check the week value is between 1 and 53
    assert 1 <= iso_cal.week <= 53

    # Check the weekday value is between 1 and 7
    assert 1 <= iso_cal.weekday <= 7
# End program