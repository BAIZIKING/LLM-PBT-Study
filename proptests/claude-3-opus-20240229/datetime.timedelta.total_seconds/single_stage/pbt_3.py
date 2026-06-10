from hypothesis import given, strategies as st
from datetime import timedelta

# Summary: Generate timedeltas by combining strategies for generating random integers 
# for the constructor parameters days, seconds, microseconds, milliseconds, 
# minutes, hours and weeks. Use both positive and negative values to test a
# wide range of inputs. Explicitly test large intervals > 270 years where
# microsecond precision may be lost.
@given(st.builds(
    timedelta,
    days=st.integers(min_value=-1000000, max_value=1000000),
    seconds=st.integers(min_value=-1000000, max_value=1000000), 
    microseconds=st.integers(min_value=-1000000, max_value=1000000),
    milliseconds=st.integers(min_value=-1000000, max_value=1000000),
    minutes=st.integers(min_value=-1000000, max_value=1000000),
    hours=st.integers(min_value=-1000000, max_value=1000000),
    weeks=st.integers(min_value=-1000000, max_value=1000000)
))
def test_timedelta_total_seconds(td):
    total_secs = td.total_seconds()
    
    # Property 1: total_seconds() should be equivalent to td / timedelta(seconds=1)
    assert total_secs == td / timedelta(seconds=1)
    
    # Property 2: total_seconds() should return a float 
    assert isinstance(total_secs, float)

    # Property 3: Very large intervals > 270 years may lose microsecond precision
    if abs(td) > timedelta(days=270*365):
        assert total_secs != td / timedelta(microseconds=1) * 1e-6
    else:
        assert total_secs == td / timedelta(microseconds=1) * 1e-6
# End program