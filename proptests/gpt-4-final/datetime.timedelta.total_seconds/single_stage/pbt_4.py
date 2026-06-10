from hypothesis import given, strategies as st
from datetime import timedelta

# Testing the timedelta.total_seconds() method
@given(st.timedeltas(min_value=timedelta(days=-10675199), max_value=timedelta(days=10675199)))
def test_timedelta_total_seconds(delta):
   
    # total_seconds function should return a float
    total_seconds_func = delta.total_seconds()
    assert isinstance(total_seconds_func, float), "Error: The function did not return a float value"
    
    # Checking the accuracy of the function, comparing it with explicit calculation
    total_seconds_calc = delta.days * 86400 + delta.seconds + delta.microseconds * 1E-6
    assert total_seconds_func == total_seconds_calc, "Error: The function did not return the accurate total seconds"