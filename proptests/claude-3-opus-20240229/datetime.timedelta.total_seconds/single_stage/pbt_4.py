from hypothesis import given, strategies as st
from datetime import timedelta

# Generate a wide variety of timedelta inputs, including:
# - Positive and negative values 
# - Zeros for some or all timedelta components (days, seconds, microseconds)
# - Very large values (> 270 years)
# - Microsecond precision
@given(
    days=st.integers(min_value=-999999999, max_value=999999999),
    seconds=st.integers(min_value=-86399, max_value=86399), 
    microseconds=st.integers(min_value=-999999, max_value=999999)
)
def test_timedelta_total_seconds(days, seconds, microseconds):
    td = timedelta(days=days, seconds=seconds, microseconds=microseconds)
    
    total_secs = td.total_seconds()
    
    # Property 1: Output value equals td / timedelta(seconds=1)
    assert total_secs == td / timedelta(seconds=1)
    
    # Property 2: Very large time intervals may lose microsecond precision
    if abs(days) > 270 * 365:
        assert total_secs == pytest.approx(td / timedelta(seconds=1), 1e-6)
    else:
        assert total_secs == td / timedelta(seconds=1)
# End program