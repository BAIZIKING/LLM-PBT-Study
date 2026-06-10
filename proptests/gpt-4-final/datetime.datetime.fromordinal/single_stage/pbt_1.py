from hypothesis import given, strategies as st
from datetime import datetime

#given creates random inputs for the function within the specified range, which is from 1 to maximum ordinal that can be represented.
@given(st.integers(min_value=1, max_value=datetime.max.toordinal())) 
def test_datetime_fromordinal(ordinal): 
    dt = datetime.fromordinal(ordinal)
    #checking if the function returns the datetime with hour, minute, second and microsecond as 0 and tzinfo as None.
    assert dt.hour == 0
    assert dt.minute == 0
    assert dt.second == 0
    assert dt.microsecond == 0
    assert dt.tzinfo is None