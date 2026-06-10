from hypothesis import given, strategies as st
from dateutil.parser import parse
import datetime

# Summary: Generate arbitrary strings and test that the parser can parse them into datetime objects or tuples.
@given(st.data())
def test_dateutil_parser_parse(data):
    # Generate a string that mimics a common date-time format
    timestr = data.draw(st.text(min_size=10, max_size=30))

    # Attempt to parse the string
    try:
        result = parse(timestr)

        # Check the type of the result
        assert isinstance(result, datetime.datetime) or (
            isinstance(result, tuple) and isinstance(result[0], datetime.datetime)
        )

        # If the result is a tuple, check the second element
        if isinstance(result, tuple):
            assert all(isinstance(token, str) for token in result[1])

    except (ValueError, OverflowError):
        pass  # It's allowed to raise these exceptions for invalid strings

# End program