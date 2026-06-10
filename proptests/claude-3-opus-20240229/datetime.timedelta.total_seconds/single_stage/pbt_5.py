from hypothesis import given, strategies as st
from datetime import timedelta

# Summary: Generate timedeltas with a wide range of values for 
# days, seconds, microseconds (both positive and negative). 
# Very large intervals (> 270 years) are also generated to test 
# loss of microsecond accuracy. The test checks that:
# 1. total_seconds() returns a float 
# 2. total_seconds() equals td / timedelta(seconds=1)
# 3. Microsecond accuracy loss occurs for intervals > 270 years
@given(st.builds(
    timedelta,
    days=st.integers(min_value=-1e12, max_value=1e12), 
    seconds=st.integers(min_value=-1e12, max_value=1e12),
    microseconds=st.integers(min_value=-1e12, max_value=1e12)
))
def test_timedelta_total_seconds(td):
    total_secs = td.total_seconds()
    assert isinstance(total_secs, float)
    assert total_secs == td / timedelta(seconds=1)
    
    if abs(td) >= timedelta(days=270*365):
        td2 = timedelta(microseconds=round(total_secs * 1e6))
        assert td != td2
    else:
        td2 = timedelta(microseconds=round(total_secs * 1e6))  
        assert td == td2
# End program