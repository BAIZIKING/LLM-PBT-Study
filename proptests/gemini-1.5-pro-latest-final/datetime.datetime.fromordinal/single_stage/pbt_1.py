from hypothesis import given, strategies as st
import datetime

# Summary: Generate random integers within and outside the valid range for datetime.datetime.fromordinal
@given(st.data())
def test_datetime_datetime_fromordinal(data):
    # Generate random integers within the valid range
    valid_ordinal = data.draw(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
    
    # Generate random integers outside the valid range
    invalid_ordinal_low = data.draw(st.integers(max_value=0))
    invalid_ordinal_high = data.draw(st.integers(min_value=datetime.datetime.max.toordinal() + 1))

    # Test valid input
    result = datetime.datetime.fromordinal(valid_ordinal)
    assert isinstance(result, datetime.datetime)
    assert result.hour == result.minute == result.second == result.microsecond == 0
    assert result.tzinfo is None

    # Test edge cases
    datetime.datetime.fromordinal(1)
    datetime.datetime.fromordinal(datetime.datetime.max.toordinal())

    # Test invalid input 
    with pytest.raises(ValueError):
        datetime.datetime.fromordinal(invalid_ordinal_low)
    with pytest.raises(ValueError):
        datetime.datetime.fromordinal(invalid_ordinal_high)
# End program