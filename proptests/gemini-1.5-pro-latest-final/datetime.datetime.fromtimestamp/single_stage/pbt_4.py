from hypothesis import given, strategies as st
import datetime

# Summary: Generates random timestamps and timezones (including None and invalid ones)
@given(st.data())
def test_datetime_fromtimestamp(data):
    timestamp = data.draw(st.floats(allow_nan=False))
    
    # Generate timezones with a bias towards None and valid ones
    tz_strategy = st.one_of(
        st.none(),
        st.sampled_from(datetime.timezone),
        st.text().map(lambda x: x)  # Generate invalid timezones
    )
    tz = data.draw(tz_strategy)

    try:
        dt_obj = datetime.datetime.fromtimestamp(timestamp, tz=tz)

        assert isinstance(dt_obj, datetime.datetime)

        if tz is None:
            assert dt_obj.tzinfo is None
        else:
            assert dt_obj.tzinfo == tz

    except OverflowError:
        # Check if timestamp is outside supported range
        pass  
    except OSError:
        # Check for localtime/gmtime failures
        pass

# End program