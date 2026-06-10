from hypothesis import given, strategies as st
from datetime import datetime

# Summary: Generates random ordinals within/outside valid range and edge cases
@given(st.data())
def test_datetime_fromordinal(data):
    # Generate random integer within valid range and edge cases
    ordinal = data.draw(st.integers(min_value=1, max_value=datetime.max.toordinal()))
    # Explicitly test minimum and maximum values
    ordinal = data.draw(st.sampled_from([1, datetime.max.toordinal(), 0, datetime.max.toordinal() + 1]))

    if 1 <= ordinal <= datetime.max.toordinal():
        dt_obj = datetime.fromordinal(ordinal)
        assert isinstance(dt_obj, datetime)
        assert dt_obj.hour == dt_obj.minute == dt_obj.second == dt_obj.microsecond == 0
        assert dt_obj.tzinfo is None
    else:
        with pytest.raises(ValueError):
            datetime.fromordinal(ordinal)
# End program