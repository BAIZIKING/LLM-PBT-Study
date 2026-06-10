from hypothesis import given, strategies as st
import datetime

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_datetime_fromordinal(ordinal):
    datetime_obj = datetime.datetime.fromordinal(ordinal)

    # Test that the fromordinal method correctly represents the datetime object
    assert datetime_obj.toordinal() == ordinal

    # Test that the time for the datetime object is 0 hours, 0 minutes, 0 seconds and 0 microseconds
    assert datetime_obj.time() == datetime.time(0, 0, 0, 0)

    # Test that tzinfo of the datetime object is None
    assert datetime_obj.tzinfo is None

# End program