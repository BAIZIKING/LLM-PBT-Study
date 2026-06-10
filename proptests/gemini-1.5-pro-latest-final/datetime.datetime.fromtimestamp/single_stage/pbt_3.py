from hypothesis import given, strategies as st
import datetime

# Summary: Generates timestamps within a wide range, including edge cases, 
# and combines them with None and various timezones to test fromtimestamp.
@given(timestamp=st.one_of(
            st.floats(allow_nan=False, allow_infinity=False),
            st.floats(min_value=-2**32, max_value=2**32),  # Around documented limits
            st.floats(min_value=1672531199, max_value=1672531201)  # Around a leap second
        ),
       tz=st.one_of(st.none(), st.timezones()))
def test_datetime_fromtimestamp(timestamp, tz):
    try:
        dt_obj = datetime.datetime.fromtimestamp(timestamp, tz=tz)
        
        # Type check
        assert isinstance(dt_obj, datetime.datetime)
        
        # Consistency
        assert dt_obj == datetime.datetime.fromtimestamp(timestamp, tz=tz)

        # Naive vs Aware
        if tz is None:
            assert dt_obj.tzinfo is None
        else:
            assert dt_obj.tzinfo == tz

    except OverflowError:
        # Expected for out-of-range timestamps
        pass
# End program