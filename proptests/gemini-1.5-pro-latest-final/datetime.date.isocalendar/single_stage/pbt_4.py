from hypothesis import given, strategies as st
from datetime import date, timedelta

# Summary: Generate diverse dates, including leap years and edge cases, and verify ISO calendar properties.
@given(
    year=st.integers(min_value=1, max_value=9999),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=31),  # Adjusted below based on month/year
)
def test_datetime_date_isocalendar(year, month, day):
    try:
        # Create date object, handling invalid day values
        test_date = date(year, month, day)
    except ValueError:
        # Skip invalid dates
        return

    # Adjust day for months with fewer than 31 days
    max_day = (date(year, month + 1, 1) - timedelta(days=1)).day
    day = min(day, max_day)
    test_date = date(year, month, day)

    result = test_date.isocalendar()

    # Check tuple structure
    assert isinstance(result, date.IsoCalendarDate)
    assert hasattr(result, "year")
    assert hasattr(result, "week")
    assert hasattr(result, "weekday")

    # Check week and weekday ranges
    assert 1 <= result.week <= 53
    assert 1 <= result.weekday <= 7

    # Check consistency for consecutive days
    if day < max_day:
        next_day_result = (test_date + timedelta(days=1)).isocalendar()
        if result.weekday == 7:
            assert next_day_result.week == result.week + 1
            assert next_day_result.weekday == 1
        else:
            assert next_day_result.week == result.week
            assert next_day_result.weekday == result.weekday + 1

# End program