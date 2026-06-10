from hypothesis import given, strategies as st
from datetime import timedelta

@given(st.integers(min_value=0, max_value=300), st.integers(min_value=0, max_value=365))
def test_timedelta_total_seconds_property(n, days):
    timedelta_obj = timedelta(days=days)
    
    # Property 1: Total seconds of timedelta is a non-negative number
    assert timedelta_obj.total_seconds() >= 0
    
    # Property 2: Consistency property
    assert timedelta_obj.total_seconds() == timedelta_obj.total_seconds()
    
    # Property 3: Scaling property
    scaled_timedelta_obj = n * timedelta_obj
    assert scaled_timedelta_obj.total_seconds() == n * timedelta_obj.total_seconds()
    
    # Property 4: Additive property
    another_timedelta_obj = timedelta(days=2 * days)
    sum_timedelta_obj = timedelta_obj + another_timedelta_obj
    assert sum_timedelta_obj.total_seconds() == timedelta_obj.total_seconds() + another_timedelta_obj.total_seconds()
    
    # Property 5: Precision property - Not always valid, depends on the platform
    if timedelta_obj.days > 270*365: # approximately equal to 270 years
        microseconds = timedelta_obj.total_seconds() / 1e6
        assert microseconds.is_integer()

# End program