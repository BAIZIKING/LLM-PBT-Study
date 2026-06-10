import datetime
from hypothesis import given, settings
from hypothesis.strategies import floats

@settings(deadline=None)
@given(floats(min_value=-float("inf"), max_value=float("inf"), allow_infinity=True, allow_nan=False))
def test_datetime_fromtimestamp(timestamp):
    try:
        # Generate a datetime object from the timestamp
        result = datetime.datetime.fromtimestamp(timestamp)
    except OverflowError:
        # If the generated timestamp is too large, we will get an OverflowError
        # Assert that this is the case
        assert timestamp > 1e10 or timestamp < -1e10
    except OSError:
        # Assert that an OSError is only thrown when the timestamp is too large
        # or too small
        assert timestamp < -1e10 or timestamp > 1e10
    else:
        # Generate a datetime object from the timestamp using the time module
        expected = datetime.datetime(*time.localtime(timestamp)[:6])

        # Assert that the obtained datetime object is the same as the expected datetime object
        assert result == expected
# End program