from hypothesis import given, strategies as st
from datetime import timedelta

# Summary: We generate timedelta instances to test timedelta.total_seconds(). 
# We hypothesize timedelta instances, considering various edge cases and ordinary timedelta intervals.
@given(st.from_type(timedelta))
def test_timedelta_total_seconds(timedelta_instance):
    total_seconds = timedelta_instance.total_seconds()
    # Property: The total_seconds must always be a non-negative float.
    assert isinstance(total_seconds, float)
    assert total_seconds >= 0
# End program