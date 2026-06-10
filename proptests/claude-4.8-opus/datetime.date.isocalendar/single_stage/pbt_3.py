from hypothesis import given, strategies as st
from datetime import date

# Summary: Generate arbitrary date objects spanning the full supported range
# (date.min to date.max), naturally covering year boundaries, leap years,
# and 53-week years. Verify the returned named tuple's structure, the valid
# ranges of week/weekday, ISO-vs-Gregorian year proximity, and round-trip
# consistency with date.fromisocalendar().
@given(st.data())
def test_datetime_date_isocalendar(data):
    d = data.draw(st.dates())

    result = d.isocalendar()

    # Property 1: Result behaves like a 3-element tuple with named fields
    assert len(result) == 3
    iso_year, iso_week, iso_weekday = result
    assert result.year == iso_year
    assert result.week == iso_week
    assert result.weekday == iso_weekday

    # Property 2: Week is between 1 and 53
    assert 1 <= iso_week <= 53

    # Property 3: Weekday is between 1 (Monday) and 7 (Sunday)
    assert 1 <= iso_weekday <= 7

    # Property 4: ISO year differs from Gregorian year by at most 1
    assert abs(iso_year - d.year) <= 1

    # Property 5: Round-trip consistency via fromisocalendar
    reconstructed = date.fromisocalendar(iso_year, iso_week, iso_weekday)
    assert reconstructed == d
# End program