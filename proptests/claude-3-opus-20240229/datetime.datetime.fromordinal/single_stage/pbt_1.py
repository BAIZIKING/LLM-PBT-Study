from hypothesis import given, strategies as st
from datetime import datetime

# Strategy: 
# - Generate ordinals in valid range [1, datetime.max.toordinal()]
# - Also generate some invalid ordinals outside this range to test exceptions
# Properties to check:
# - Result is a datetime object
# - Year, month, day match expected values based on ordinal
# - Hour, minute, second, microsecond are all 0
# - tzinfo is None
# - Invalid ordinals raise ValueError
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