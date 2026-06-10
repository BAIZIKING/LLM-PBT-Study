from hypothesis import given, strategies as st
from datetime import date

# Summary: Generate arbitrary date objects across the full valid range
# (year 1 to 9999) using st.dates(), which naturally covers year-boundary
# edge cases, leap years, and min/max dates. Then verify structural and
# range invariants of the isocalendar() named tuple, plus round-trip
# consistency with date.fromisocalendar.
@given(st.data())
def test_datetime_date_isocalendar():
    d = st.data().draw(st.dates())  # placeholder; real draw below

@given(d=st.dates())
def test_datetime_date_isocalendar(d):
    result = d.isocalendar()

    # Property 1: Result is a named tuple with three named components.
    assert hasattr(result, "year")
    assert hasattr(result, "week")
    assert hasattr(result, "weekday")
    assert len(result) == 3
    assert (result.year, result.week, result.weekday) == tuple(result)

    iso_year, iso_week, iso_weekday = result

    # Property 2: weekday is in [1, 7] (Monday=1 .. Sunday=7).
    assert 1 <= iso_weekday <= 7

    # Property 3: week number is in [1, 53] (ISO years have 52 or 53 weeks).
    assert 1 <= iso_week <= 53

    # Property 4: ISO year differs from Gregorian year by at most 1,
    # since only days near a year boundary roll into an adjacent ISO year.
    assert abs(iso_year - d.year) <= 1

    # Property 5: Round-trip consistency — reconstructing the date from its
    # ISO calendar components must yield the original date.
    assert date.fromisocalendar(iso_year, iso_week, iso_weekday) == d
# End program