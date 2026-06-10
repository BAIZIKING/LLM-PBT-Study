from hypothesis import given, strategies as st
import datetime

@given(ordinal=st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_datetime_fromordinal_properties(ordinal):
    dt = datetime.datetime.fromordinal(ordinal)
    
    # Property 1: The returned datetime object should have the same ordinal as the input ordinal.
    assert dt.toordinal() == ordinal
    
    # Property 2: The returned datetime object should have the hour, minute, second, and microsecond all set to 0.
    assert dt.hour == 0
    assert dt.minute == 0
    assert dt.second == 0
    assert dt.microsecond == 0
    
    # Property 3: The returned datetime object should have tzinfo set to None.
    assert dt.tzinfo is None
    
    # Property 4: Calling fromordinal with the same ordinal multiple times should return equal datetime objects.
    dt2 = datetime.datetime.fromordinal(ordinal)
    assert dt == dt2
    
    # Property 5: Calling fromordinal with an ordinal outside the valid range should raise a ValueError.
    with pytest.raises(ValueError):
        datetime.datetime.fromordinal(0)
    with pytest.raises(ValueError):
        datetime.datetime.fromordinal(datetime.datetime.max.toordinal() + 1)
# End program