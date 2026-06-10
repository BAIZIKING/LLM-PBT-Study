from hypothesis import given, strategies as st
import datetime
import pytz

# Summary: Generates timestamps and timezones, checking for expected behavior and errors.
@given(st.data())
def test_datetime_fromtimestamp(data):
    # Generate timestamps: normal range, edge cases, extreme values
    timestamp = data.draw(st.floats(
        min_value=-1e15,  # Extreme low value
        max_value=1e15,   # Extreme high value
        allow_nan=False,  # Avoid NaN values
        allow_infinity=False  # Avoid infinity values
    ))

    # Generate timezones: None or valid pytz timezones
    timezone = data.draw(st.one_of(
        st.none(),
        st.sampled_from(pytz.all_timezones)
    ))

    try:
        dt_obj = datetime.datetime.fromtimestamp(timestamp, tz=timezone)

        # Check return type
        assert isinstance(dt_obj, datetime.datetime)

        # Check naive/aware based on timezone
        assert dt_obj.tzinfo is None if timezone is None else dt_obj.tzinfo is not None

        # Check consistency for same inputs
        assert dt_obj == datetime.datetime.fromtimestamp(timestamp, tz=timezone)

    except OverflowError:
        # Expect OverflowError for out-of-range timestamps
        pass

# End program