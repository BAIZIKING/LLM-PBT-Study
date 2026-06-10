from hypothesis import given, strategies as st
from datetime import timedelta

# Summary: Generate a wide range of timedelta objects, including edge cases, to thoroughly test the total_seconds() method.

@given(st.builds(timedelta,
                 days=st.integers(min_value=-100_000, max_value=100_000),
                 seconds=st.integers(min_value=-100_000, max_value=100_000),
                 microseconds=st.integers(min_value=-100_000, max_value=100_000),
                 milliseconds=st.integers(min_value=-100_000, max_value=100_000),
                 minutes=st.integers(min_value=-100_000, max_value=100_000),
                 hours=st.integers(min_value=-100_000, max_value=100_000),
                 weeks=st.integers(min_value=-100_000, max_value=100_000)))
def test_timedelta_total_seconds(td):
    # Property 1: total_seconds() should return a floating-point value.
    assert isinstance(td.total_seconds(), float)

    # Property 2: The result should be consistent with manual calculation.
    expected_seconds = td.days * 86400 + td.seconds + td.microseconds * 1e-6 + \
                       td.milliseconds * 1e-3 + td.minutes * 60 + td.hours * 3600 + td.weeks * 604800
    assert abs(td.total_seconds() - expected_seconds) < 1e-6  # Allow for small floating-point discrepancies
# End program