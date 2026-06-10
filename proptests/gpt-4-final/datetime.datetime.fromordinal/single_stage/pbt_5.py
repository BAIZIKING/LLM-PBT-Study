import datetime
from hypothesis import given, strategies as st

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_fromordinal(ordinal):
    dt = datetime.datetime.fromordinal(ordinal)

    #Check if returned value is a datetime instance
    assert isinstance(dt, datetime.datetime)
    
    #Check if the hour, minute, second, and microsecond are 0
    assert dt.hour == 0 and dt.minute == 0 and dt.second == 0 and dt.microsecond == 0
    
    #Check if tzinfo is None
    assert dt.tzinfo is None
# End program