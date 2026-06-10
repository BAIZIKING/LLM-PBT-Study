from hypothesis import given, strategies as st
from datetime import datetime

# Summary: Generate valid ordinal dates between 1 and datetime.max.toordinal() (inclusive).
# Also generate some invalid ordinal dates less than 1 and greater than datetime.max.toordinal().
# Check that:
#  1) Valid ordinal dates return a datetime object
#  2) The returned datetime has hour, minute, second, microsecond of 0 and tzinfo of None
#  3) Invalid ordinal dates raise a ValueError
@given(st.integers(min_value=-1000, max_value=datetime.max.toordinal()+1000))
def test_datetime_fromordinal(ordinal):
    if 1 <= ordinal <= datetime.max.toordinal():
        dt = datetime.fromordinal(ordinal)
        assert isinstance(dt, datetime)
        assert dt.hour == 0
        assert dt.minute == 0 
        assert dt.second == 0
        assert dt.microsecond == 0
        assert dt.tzinfo is None
    else:
        try:
            dt = datetime.fromordinal(ordinal)
            assert False, "Expected ValueError for invalid ordinal"
        except ValueError:
            pass
# End program