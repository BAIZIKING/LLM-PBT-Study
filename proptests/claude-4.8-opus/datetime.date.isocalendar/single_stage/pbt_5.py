from datetime import date
from hypothesis import given, strategies as st

# Summary: Generate arbitrary datetime.date objects across the full valid
# range using st.dates(), which naturally covers year boundaries, leap years,
# 53-week ISO years, and the extreme min/max dates.
@given(st.data())
def test_datetime_date_isocalendar():
    d = st.data().draw(st.dates())

    result = d.isocalendar()

    # Property 1: result is a named tuple with year, week, weekday
    assert len(result) == 3
    assert result.year == result[0]
    assert result.week == result[1]
    assert result.weekday == result[2]

    iso_year, iso_week, iso_weekday = result

    # Property 2: ISO week is between 1 and 53 inclusive
    assert 1 <= iso_week <= 53

    # Property 3: ISO weekday is between 1 (Mon) and 7 (Sun) inclusive
    assert 1 <= iso_weekday <= 7

    # Property 4: ISO year differs from Gregorian year by at most 1
    assert abs(iso_year - d.year) <= 1

    # Property 5: round-trip via fromisocalendar reconstructs the date
    assert date.fromisocalendar(iso_year, iso_week, iso_weekday) == d
# End program