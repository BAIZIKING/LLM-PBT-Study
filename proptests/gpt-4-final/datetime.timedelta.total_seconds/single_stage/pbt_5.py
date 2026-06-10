from hypothesis import given, strategies as st
from datetime import timedelta

@st.composite
def timedelta_strategy(draw):
    days = draw(st.integers(min_value=0, max_value=365)) 
    seconds = draw(st.integers(min_value=0, max_value=59)) 
    microseconds = draw(st.integers(min_value=0, max_value=999999)) 
    milliseconds = draw(st.integers(min_value=0, max_value=999)) 
    minutes = draw(st.integers(min_value=0, max_value=59)) 
    hours = draw(st.integers(min_value=0, max_value=23)) 
    weeks = draw(st.integers(min_value=0, max_value=52))
    
    return timedelta(days=days, seconds=seconds, microseconds=microseconds, 
                     milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)

@given(timedelta_strategy())
def test_timedelta_total_seconds(timedelta_value):
    total_seconds = timedelta_value.total_seconds()
    assert total_seconds == (timedelta_value.microseconds + 
                            (timedelta_value.seconds + timedelta_value.days * 24*3600) * 10**6) / 10**6
    assert total_seconds >= 0