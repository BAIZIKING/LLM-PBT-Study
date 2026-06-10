from hypothesis import given, strategies as st
from datetime import timedelta

# Summary: Generate a wide range of timedelta instances with varying days, seconds, microseconds, milliseconds, minutes, hours, and weeks.
@given(st.data())
def test_datetime_timedelta_total_seconds(data):
    # Generate random values for each component of timedelta
    days = data.draw(st.integers(min_value=-10**6, max_value=10**6))  # Test large time intervals
    seconds = data.draw(st.integers(min_value=0, max_value=86400))  # Within a day's range
    microseconds = data.draw(st.integers(min_value=0, max_value=10**6))
    milliseconds = data.draw(st.integers(min_value=0, max_value=10**3))
    minutes = data.draw(st.integers(min_value=0, max_value=1440))  # Within a day's range
    hours = data.draw(st.integers(min_value=0, max_value=24))  # Within a day's range
    weeks = data.draw(st.integers(min_value=-52 * 100, max_value=52 * 100))  # Test large time intervals

    # Create a timedelta instance
    time_delta = timedelta(days=days, seconds=seconds, microseconds=microseconds,
                           milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)

    # Calculate total seconds using total_seconds()
    total_seconds = time_delta.total_seconds()

    # Assert that total_seconds is non-negative
    assert total_seconds >= 0

    # Assert that total_seconds aligns with the expected calculation
    expected_seconds = (days * 86400) + seconds + (microseconds / 10**6) + (milliseconds / 10**3) + (minutes * 60) + (hours * 3600) + (weeks * 7 * 86400)
    assert abs(total_seconds - expected_seconds) < 1e-6  # Account for potential floating-point precision errors
# End program