from hypothesis import given, strategies as st
import datetime

# Summary: The generation strategy aims to create a diverse range of timedelta objects to test the total_seconds() method comprehensively. 
# It covers various durations, including:
# - Positive and negative timedeltas.
# - Timedeltas with different units (days, seconds, microseconds, etc.).
# - Timedeltas close to zero and very large timedeltas.
# - Timedeltas that might trigger edge cases, such as those exceeding 270 years.
@given(st.data())
def test_datetime_timedelta_total_seconds(data):
    # Generate random values for days, seconds, microseconds, milliseconds, minutes, hours, and weeks.
    days = data.draw(st.integers(min_value=-100000, max_value=100000))  # Cover a wide range of days, including negative values.
    seconds = data.draw(st.integers(min_value=0, max_value=86400))  # Range of seconds within a day.
    microseconds = data.draw(st.integers(min_value=0, max_value=1000000))  # Range of microseconds within a second.
    milliseconds = data.draw(st.integers(min_value=0, max_value=1000))  # Range of milliseconds within a second.
    minutes = data.draw(st.integers(min_value=0, max_value=1440))  # Range of minutes within a day.
    hours = data.draw(st.integers(min_value=0, max_value=24))  # Range of hours within a day.
    weeks = data.draw(st.integers(min_value=-1000, max_value=1000))  # Range of weeks, including negative values.

    # Create a timedelta object using the generated values.
    td = datetime.timedelta(days=days, seconds=seconds, microseconds=microseconds, milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)

    # Calculate the total seconds using the total_seconds() method.
    total_seconds = td.total_seconds()

    # Verify properties based on the API documentation:
    # 1. Check if total_seconds is a floating-point number.
    assert isinstance(total_seconds, float)

    # 2. Check if the sign of total_seconds matches the sign of the timedelta.
    assert (total_seconds > 0 and td > datetime.timedelta(0)) or (total_seconds < 0 and td < datetime.timedelta(0)) or (total_seconds == 0 and td == datetime.timedelta(0))

    # 3. For timedeltas within a reasonable range (less than 270 years), compare the calculated total_seconds with an independently computed value using basic arithmetic.
    if abs(td.days) < 270 * 365:
        expected_total_seconds = td.days * 86400 + td.seconds + td.microseconds / 1000000
        assert abs(total_seconds - expected_total_seconds) < 1e-6  # Allow for small discrepancies due to floating-point precision.
# End program