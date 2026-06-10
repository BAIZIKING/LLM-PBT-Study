from datetime import timedelta
from hypothesis import given, strategies as st

# We will generate inputs for timedelta with random values for days, hours, minutes, and seconds.
# We then check if the total_seconds method return the right values and if it loses accuracy for very large inputs.
@given(
    days=st.integers(min_value=0, max_value=10**6), 
    hours=st.integers(min_value=0, max_value=23), 
    minutes=st.integers(min_value=0, max_value=59), 
    seconds=st.integers(min_value=0, max_value=59)
)
def test_datetime_timedelta_total_seconds(days, hours, minutes, seconds):
    td = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    assert td.total_seconds() == days * 24 * 3600 + hours * 3600 + minutes * 60 + seconds

    # Check for large interval units
    if days > 365 * 270:  # More than 270 years
        assert td.total_seconds() % 1 == 0  # Check if we have lost the microsecond accuracy
# End program