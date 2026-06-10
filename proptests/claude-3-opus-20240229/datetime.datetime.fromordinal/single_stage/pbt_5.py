from hypothesis import given, strategies as st
from datetime import datetime

# Summary: Generate valid ordinal dates between 1 and datetime.max.toordinal() 
# inclusive. Also generate invalid ordinal dates below 1 and above 
# datetime.max.toordinal() to test error handling. Check that:
# 1) Valid ordinals produce datetime objects 
# 2) The ordinal of the returned datetime equals the input ordinal
# 3) Hour, minute, second and microsecond are 0 and tzinfo is None
# 4) Invalid ordinals raise a ValueError
@given(st.integers(min_value=-1000, max_value=datetime.max.toordinal()+1000))
def test_datetime_fromordinal(ordinal):
    if 1 <= ordinal <= datetime.max.toordinal():
        dt = datetime.fromordinal(ordinal)
        assert isinstance(dt, datetime)
        assert dt.toordinal() == ordinal
        assert dt.hour == dt.minute == dt.second == dt.microsecond == 0
        assert dt.tzinfo is None
    else:
        try:
            datetime.fromordinal(ordinal)
            assert False, "Expected ValueError for invalid ordinal"
        except ValueError:
            pass
# End program