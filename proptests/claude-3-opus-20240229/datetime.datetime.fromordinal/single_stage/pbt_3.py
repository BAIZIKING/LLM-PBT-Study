from hypothesis import given, strategies as st
from datetime import datetime

# Summary: 
# Generate valid ordinal values between 1 and datetime.max.toordinal()
# Also generate some invalid values outside this range to check for ValueError
# For each generated ordinal, construct a datetime using fromordinal
# Check that the resulting datetime has the expected properties:
#   - year, month, day should match the proleptic Gregorian calendar for the ordinal
#   - hour, minute, second, microsecond should all be 0
#   - tzinfo should be None
@given(st.integers(min_value=-1000, max_value=datetime.max.toordinal()+1000))
def test_datetime_fromordinal(ordinal):
    if 1 <= ordinal <= datetime.max.toordinal():
        dt = datetime.fromordinal(ordinal)
        assert dt.toordinal() == ordinal
        assert dt.hour == dt.minute == dt.second == dt.microsecond == 0
        assert dt.tzinfo is None
    else:
        try:
            dt = datetime.fromordinal(ordinal)
            assert False, "Expected ValueError for invalid ordinal"
        except ValueError:
            pass
# End program