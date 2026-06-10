from hypothesis import given, strategies as st
from datetime import timedelta

# Summary: Generate a wide variety of timedelta values to test total_seconds()
# - Use st.builds() to construct timedelta from random arguments 
# - Generate years, days, seconds, microseconds, milliseconds, minutes, hours, weeks
# - Include min/max for some args to test extremes (e.g. 0 to 270 years)
# - Sample some special timedelta values like 0 and large intervals
# Properties to test:
# - total_seconds() matches manual calculation of total seconds
# - Very large intervals may lose microsecond precision but not second precision
@given(st.builds(timedelta,
    days=st.integers(min_value=0, max_value=270*365), 
    seconds=st.integers(min_value=0, max_value=24*3600-1),
    microseconds=st.integers(min_value=0, max_value=1e6-1),
    milliseconds=st.integers(min_value=0, max_value=1000-1),
    minutes=st.integers(min_value=0, max_value=60-1), 
    hours=st.integers(min_value=0, max_value=24-1),
    weeks=st.integers(min_value=0, max_value=52)) | 
        st.sampled_from([timedelta(0), timedelta(days=1e9)]))
def test_timedelta_total_seconds(td):
    total_secs = td / timedelta(seconds=1) 
    assert td.total_seconds() == total_secs
    
    total_micro = td / timedelta(microseconds=1)
    assert abs(td.total_seconds() - total_micro * 1e-6) < 1e-7
# End program