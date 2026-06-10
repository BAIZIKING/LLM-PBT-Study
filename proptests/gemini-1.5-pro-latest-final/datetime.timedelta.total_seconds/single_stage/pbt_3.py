from hypothesis import given, strategies as st
from datetime import timedelta

# Summary: The strategy aims to generate a wide range of timedelta objects, including edge cases, to thoroughly test the total_seconds() method.

# 1. Generate days: We generate a wide range of days, including negative values, zero, and large values to test boundary conditions and potential overflow issues.

# 2. Generate seconds and microseconds: Similar to days, we generate a range of values for seconds and microseconds, including negative, zero, and large positive values. This helps test the method's handling of different time components and their interactions.

# 3. Combine components: We combine the generated days, seconds, and microseconds to create timedelta objects. This ensures diverse input combinations for testing.

@given(st.data())
def test_datetime_timedelta_total_seconds(data):
    days = data.draw(st.integers(min_value=-100000, max_value=100000))  # Generate a wide range of days
    seconds = data.draw(st.integers(min_value=-100000, max_value=100000))  # Generate a wide range of seconds
    microseconds = data.draw(st.integers(min_value=-1000000, max_value=1000000))  # Generate a wide range of microseconds

    td = timedelta(days=days, seconds=seconds, microseconds=microseconds)

    # Properties to check:

    # 1. Total seconds calculation: We verify if the total_seconds() method returns the expected total number of seconds based on the timedelta components. 
    # This ensures accurate conversion and calculation.

    # 2. Consistency: We check if dividing the timedelta by timedelta(seconds=1) yields the same result as total_seconds().
    # This confirms consistency with the documentation's description of the method's behavior.

    # 3. Microsecond accuracy: For timedeltas smaller than 270 years, we compare the total_seconds() result with a more precise calculation
    # involving microseconds to verify accuracy within the documented limits.

    total_seconds_expected = days * 86400 + seconds + microseconds / 1000000
    assert abs(td.total_seconds() - total_seconds_expected) < 1e-6  # Allow for small floating-point discrepancies

    assert td.total_seconds() == (td / timedelta(seconds=1)).total_seconds()  # Check consistency with division

    if abs(days) < 270 * 365:  # Check microsecond accuracy for timedeltas within documented limits
        assert abs(td.total_seconds() - (td / timedelta(microseconds=1))) < 1e-6
# End program