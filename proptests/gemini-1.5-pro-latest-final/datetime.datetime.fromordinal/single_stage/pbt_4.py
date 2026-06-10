from hypothesis import given, strategies as st
import datetime

# Summary: Generate a wide range of integers, including edge cases, to test datetime.datetime.fromordinal
@given(st.integers() | st.just(1) | st.just(datetime.datetime.max.toordinal()))
def test_datetime_fromordinal(ordinal):
    if 1 <= ordinal <= datetime.datetime.max.toordinal():
        dt_obj = datetime.datetime.fromordinal(ordinal)
        assert isinstance(dt_obj, datetime.datetime)
        assert dt_obj.hour == dt_obj.minute == dt_obj.second == dt_obj.microsecond == 0
        assert dt_obj.tzinfo is None
    else:
        with pytest.raises(ValueError):
            datetime.datetime.fromordinal(ordinal)
# End program