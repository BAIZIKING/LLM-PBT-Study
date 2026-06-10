from hypothesis import given, strategies as st
from datetime import datetime

# Generate a wide variety of valid ordinal values, including edge cases like 1 and datetime.max.toordinal().
# Also generate some invalid values outside the valid range to check for ValueErrors.
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
            dt = datetime.fromordinal(ordinal)
            assert False, "Expected ValueError for invalid ordinal"
        except ValueError:
            pass
# End program