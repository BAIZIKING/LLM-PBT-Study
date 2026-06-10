from hypothesis import given, strategies as st
import datetime
import pytz  # Assuming pytz is installed

# Summary: Generates timestamps and optional timezones to test datetime.datetime.fromtimestamp
@given(st.data())
def test_datetime_fromtimestamp(data):
    # Generate timestamps: normal range, edge cases, and out-of-range
    timestamp = data.draw(st.one_of(
        st.floats(min_value=-2**31, max_value=2**31-1),  # Typical range
        st.floats(min_value=-2**63, max_value=-2**31-1),  # Out of range (negative)
        st.floats(min_value=2**31, max_value=2**63-1)     # Out of range (positive)
    ))
    
    # Generate optional timezones: None or a random tzinfo
    tz = data.draw(st.one_of(
        st.none(),
        st.builds(pytz.timezone, st.sampled_from(pytz.all_timezones_set))
    ))

    try:
        dt_obj = datetime.datetime.fromtimestamp(timestamp, tz)

        # Check output type
        assert isinstance(dt_obj, datetime.datetime)

        # Check naive/aware datetime based on tz
        assert dt_obj.tzinfo is None if tz is None else dt_obj.tzinfo == tz

    except OverflowError:
        # Check OverflowError for out-of-range timestamps
        assert timestamp < -2**31 or timestamp >= 2**31

# End program