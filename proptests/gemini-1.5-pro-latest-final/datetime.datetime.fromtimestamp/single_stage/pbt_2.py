from hypothesis import given, strategies as st
import datetime
import pytz

# Summary: Generates a variety of timestamps and timezones to test datetime.datetime.fromtimestamp
@given(st.data())
def test_datetime_fromtimestamp(data):
    # Generate timestamps
    timestamp = data.draw(
        st.one_of(
            st.floats(allow_nan=False, allow_infinity=False),
            st.integers(),
            st.just(0),
            st.just(datetime.MINYEAR),
            st.just(datetime.MAXYEAR)
        )
    )

    # Generate timezones
    tz = data.draw(
        st.one_of(
            st.none(),
            st.just(datetime.timezone.utc),
            st.builds(datetime.timezone, st.timedeltas()),
            st.sampled_from(pytz.all_timezones)  # Requires pytz package
        )
    )

    # Check for OverflowError
    if not (datetime.MINYEAR <= timestamp <= datetime.MAXYEAR):
        with pytest.raises(OverflowError):
            datetime.datetime.fromtimestamp(timestamp, tz)
        return

    # Test datetime creation and properties
    try:
        dt = datetime.datetime.fromtimestamp(timestamp, tz)
        assert isinstance(dt, datetime.datetime)
        
        if tz is None:
            assert dt.tzinfo is None
        else:
            assert dt.tzinfo == tz

        # Further assertions for specific timestamp and tz combinations can be added here
        
    except OSError:
        # Handle potential OSError cases
        pass

# End program