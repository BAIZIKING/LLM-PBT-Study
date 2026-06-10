from hypothesis import given, strategies as st
from datetime import datetime

# We'll generate ordinals from 1 till the maximum possible ordinal
# We expect that when we convert these ordinals back to datetime and then back to ordinal we get the same value
@given(st.integers(min_value=1, max_value=datetime.max.toordinal()))
def test_datetime_fromordinal(ordinal):
    dt = datetime.fromordinal(ordinal)
    # Check if the result is a datetime instance
    assert isinstance(dt, datetime)
    # Check if converting the datetime back to ordinal gives the original ordinal
    assert dt.toordinal() == ordinal