from hypothesis import given, strategies as st
from datetime import date

# Summary: Generate arbitrary date objects across the full supported range
# (year 1 to 9999) using st.dates(), naturally covering year boundaries,
# leap years, and min/max edge cases where ISO year diverges from Gregorian year.
@given(st.data())
def test_datetime_date_isocalendar():
    d = st.data().draw(st.dates())

    result = d.isocalendar()

    # Property 1: named tuple with year, week, weekday
    assert len(result) == 3
    assert result.year == result[0]
    assert result.week == result[1]
    assert result.weekday == result[2]

    iso_year, iso_week, iso_weekday = result

    # Property 2: week is between 1 and 53
    assert 1 <= iso_week <= 53

    # Property 3: weekday is between 1 (Monday) and 7 (Sunday)
    assert 1 <= iso_weekday <= 7

    # Property 4: ISO year is within 1 of the Gregorian year
    assert abs(iso_year - d.year) <= 1

    # Property 5: round-trip consistency via fromisocalendar
    assert date.fromisocalendar(iso_year, iso_week, iso_weekday) == d

    # Property 6: ISO weekday matches isoweekday()
    assert iso_weekday == d.isoweekday()
# End program