from hypothesis import given, strategies as st
import datetime

# Summary: Generate random integers within and outside the valid ordinal range
@given(st.integers())
def test_datetime_fromordinal(ordinal):
    # Check if ordinal is within valid range
    if 1 <= ordinal <= datetime.MAXYEAR * 365:
        # For valid input, check returned datetime properties
        dt_obj = datetime.datetime.fromordinal(ordinal)
        assert dt_obj.hour == 0
        assert dt_obj.minute == 0
        assert dt_obj.second == 0
        assert dt_obj.microsecond == 0
        assert dt_obj.tzinfo is None
    else:
        # For invalid input, expect ValueError
        with pytest.raises(ValueError):
            datetime.datetime.fromordinal(ordinal)
# End program