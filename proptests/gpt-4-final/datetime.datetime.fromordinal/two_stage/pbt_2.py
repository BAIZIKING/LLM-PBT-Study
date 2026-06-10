from hypothesis import given, strategies as st
import datetime

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_datetime_fromordinal_property(ordinal):
    dt = datetime.datetime.fromordinal(ordinal)
    
    # Property 1: Output is a datetime object
    assert isinstance(dt, datetime.datetime)

    # Property 2: The hour, minute, second, microsecond are all set to 0
    assert dt.hour == dt.minute == dt.second == dt.microsecond == 0

    # Property 3: tzinfo property of the output is None
    assert dt.tzinfo is None

@given(st.integers(max_value=0))
def test_datetime_fromordinal_value_error_low(ordinal):
    try:
        dt = datetime.datetime.fromordinal(ordinal)
    except ValueError:
        pass

@given(st.integers(min_value=datetime.datetime.max.toordinal()+1))
def test_datetime_fromordinal_value_error_high(ordinal):
    try:
        dt = datetime.datetime.fromordinal(ordinal)
    except ValueError:
        pass