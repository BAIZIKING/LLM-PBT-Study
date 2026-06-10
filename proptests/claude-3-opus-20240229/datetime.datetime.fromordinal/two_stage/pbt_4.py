from hypothesis import given, strategies as st
import datetime

@given(st.integers(min_value=1, max_value=datetime.max.toordinal()))
def test_datetime_fromordinal_properties(ordinal):
    dt = datetime.datetime.fromordinal(ordinal)
    
    # Property 1: Year should be greater than or equal to 1
    assert dt.year >= 1
    
    # Property 2: Month should be between 1 and 12, inclusive
    assert 1 <= dt.month <= 12
    
    # Property 3: Day should be between 1 and the maximum number of days in the corresponding month and year
    assert 1 <= dt.day <= (datetime.datetime(dt.year, dt.month % 12 + 1, 1) - datetime.timedelta(days=1)).day
    
    # Property 4: Hour, minute, second, and microsecond should be 0
    assert dt.hour == 0
    assert dt.minute == 0
    assert dt.second == 0
    assert dt.microsecond == 0
    
    # Property 5: tzinfo should be None
    assert dt.tzinfo is None
# End program