from hypothesis import given, strategies as st
from datetime import date

# Summary: Generate diverse dates, including leap years and edge cases, to test isocalendar() behavior.
@given(year=st.integers(min_value=1900, max_value=2100),
       month=st.integers(min_value=1, max_value=12),
       day=st.integers(min_value=1, max_value=31))
def test_date_isocalendar(year, month, day):
    try:
        input_date = date(year, month, day)
    except ValueError:
        # Skip invalid dates (e.g., Feb 30th)
        assume(False)

    result = input_date.isocalendar()

    # Check return type and component ranges
    assert isinstance(result, date.IsoCalendarDate)
    assert 1 <= result.week <= 53
    assert 1 <= result.weekday <= 7

    # Verify year alignment with ISO week date system
    jan_4th = date(result.year, 1, 4)
    _, week, _ = jan_4th.isocalendar()
    assert week == 1

    # Check weekday consistency
    expected_weekday = (input_date.weekday() + 1) % 7 + 1
    assert result.weekday == expected_weekday

# End program