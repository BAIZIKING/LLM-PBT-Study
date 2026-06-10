from hypothesis import given, strategies as st
from datetime import datetime
import dateutil.parser

# Generation strategy: Generate a wide range of valid ISO-8601 datetime strings and check
# if the function returns the correct datetime.datetime object.
@given(st.datetimes().map(lambda dt: dt.isoformat()))
def test_dateutil_parser_isoparse(date_string):
    # Parse the string using dateutil.parser.isoparse
    parsed_date = dateutil.parser.isoparse(date_string)
    
    # Create a datetime.datetime object using the same information
    dt_object = datetime.fromisoformat(date_string)
    
    assert parsed_date == dt_object
# End program