from datetime import date
from hypothesis import given, strategies as st

# Summary: Generate arbitrary datetime.date objects across the full supported
# range (0001-01-01 to 9999-12-31) using st.dates(), naturally exercising
# year/week boundaries, leap years, 52/53-week years, and min/max edge cases.
@given(st.data())
def test_datetime_date_isocalendar():
    d = st.data
    drawn = None

    # Draw a date using the provided data strategy
    @given(st.dates())
    def inner(d):
        result = d.isocalendar()

        # Property 1: result has three components
        assert len(result) == 3

        # Property 2: named-tuple attributes match positional values
        iso_year, iso_week, iso_weekday = result
        assert result.year == iso_year
        assert result.week == iso_week
        assert result.weekday == iso_weekday

        # Property 3: value ranges
        assert 1 <= iso_week <= 53
        assert 1 <= iso_weekday <= 7

        # Property 4: round-trip reconstruction yields the same date
        assert date.fromisocalendar(iso_year, iso_week, iso_weekday) == d

        # Property 5: ISO year is within 1 of the Gregorian year
        assert abs(iso_year - d.year) <= 1

    inner()
# End program