from hypothesis import given, strategies as st
import datetime
import pytz

@given(st.floats(allow_infinity=False, allow_nan=False), st.data())
def test_datetime_fromtimestamp_property(timestamp, tzinfo_object):
    # Generating tzinfo object
    tzinfo = tzinfo_object.draw(st.none() | st.sampled_from(pytz.all_timezones), label="tzinfo")

    # Converting the tzinfo to tzinfo subclass instance
    if tzinfo:
        tzinfo = pytz.timezone(tzinfo)

    try:
        # Preventing dates outside of 1970 - 2038 years range which are common restrictions for this function
        if datetime.MINYEAR <= datetime.datetime.utcfromtimestamp(timestamp).year <= datetime.MAXYEAR:
            # Calling fromtimestamp
            datetime_obj = datetime.datetime.fromtimestamp(timestamp, tzinfo)
            
            # Test: The output of the function should be an instance of the datetime.datetime class.
            assert isinstance(datetime_obj, datetime.datetime)

            # Test: If the tz argument is None or not specified, the output datetime object should reflect the platform's local date and time.
            # Test: If the tz argument is not None and it is an instance of a tzinfo subclass, the converted timestamp should match the specified time zone.
            if tzinfo is None:
                assert datetime_obj.utcoffset() is None
            else:
                assert datetime_obj.utcoffset() == tzinfo.utcoffset(datetime_obj)

            # Test: If the timestamp argument is valid, there should not be any inconsistency in the conversion.
            assert datetime.datetime.fromtimestamp(timestamp, tzinfo) == datetime_obj

    except (OverflowError, OSError):
        # Properties: Function might raise OverflowError or OSError based on the timestamp input value.
        pass

# End program