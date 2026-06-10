from hypothesis import given, strategies as st
from datetime import datetime

# Summary: Generate random integers within and outside the valid range for ordinal
@given(st.integers(min_value=0, max_value=datetime.max.toordinal() + 1))
def test_datetime_fromordinal(ordinal):
    if 1 <= ordinal <= datetime.max.toordinal():
        # Valid range: Check returned type, date components, time components, and tzinfo
        dt_obj = datetime.fromordinal(ordinal)
        assert isinstance(dt_obj, datetime)
        assert dt_obj.toordinal() == ordinal
        assert dt_obj.hour == dt_obj.minute == dt_obj.second == dt_obj.microsecond == 0
        assert dt_obj.tzinfo is None
    else:
        # Outside valid range: Expect ValueError
        with pytest.raises(ValueError):
            datetime.fromordinal(ordinal)
# End program