from hypothesis import given, strategies as st
from datetime import timedelta

# Generate a wide variety of timedelta inputs, including:
# - Positive and negative values for days, seconds, microseconds 
# - Large and small magnitudes (from microseconds to years)
# - Zeros for some or all of days, seconds, microseconds
# - Exceeding 270 years to check microsecond accuracy loss
@given(st.builds(
    timedelta,
    days=st.integers(min_value=-1000000, max_value=1000000), 
    seconds=st.integers(min_value=-1000000, max_value=1000000),
    microseconds=st.integers(min_value=-1000000, max_value=1000000)
))
def test_timedelta_total_seconds(td):
    total_secs = td.total_seconds()
    
    # Check total_seconds() equals td / timedelta(seconds=1)
    assert total_secs == td / timedelta(seconds=1)
    
    # Check int(total_seconds) equals total whole seconds
    assert int(total_secs) == td.days * 86400 + td.seconds
    
    # Check fractional part equals microseconds
    assert total_secs - int(total_secs) == td.microseconds / 1e6
    
    # Check sign matches timedelta sign
    assert (total_secs < 0) == (td.days < 0)
    
    # Check absolute value is less than 1 if zero timedelta 
    if td == timedelta(0):
        assert abs(total_secs) < 1

# End program