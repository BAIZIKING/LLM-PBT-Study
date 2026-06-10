from hypothesis import given, strategies as st
from dateutil.parser import parse
import datetime

# The generation strategy aims to test a variety of valid and potentially problematic
# date string formats. It includes:
# - Valid date strings in common formats like YYYY-MM-DD
# - Valid date strings with times
# - Valid date strings with time zone info 
# - Potentially ambiguous date strings like MM/DD/YY that test the dayfirst/yearfirst options
# - Strings with extra tokens to test the fuzzy parsing
# - Invalid date strings to check for proper error handling
@given(st.one_of(
    st.dates().map(lambda d: d.strftime('%Y-%m-%d')),  
    st.datetimes().map(lambda d: d.isoformat()),
    st.dates().map(lambda d: d.strftime('%Y-%m-%d') + ' EDT'),
    st.datetimes().map(lambda d: d.strftime('%m/%d/%y')),
    st.from_regex(r'\d{4}-\d{2}-\d{2}( \d{2}:\d{2}(:\d{2})?)?'),
    st.from_regex(r'([A-Za-z]+ )*\d{4}-\d{2}-\d{2}( \d{2}:\d{2}(:\d{2})?)?'),
    st.from_regex(r'\d{2}/\d{2}/\d{2}'),
    st.from_regex(r'[A-Za-z]+')
))
def test_dateutil_parser_parse(date_string):
    try:
        parsed_date = parse(date_string)
    except (ValueError, OverflowError):
        # Raises expected exceptions for invalid input
        parsed_date = None
    
    if parsed_date is not None:
        # If parsing succeeds, check the return value is a datetime
        assert isinstance(parsed_date, datetime.datetime)

        # If date_string included a full ISO timestamp, parsed_date should match it 
        if len(date_string) >= 19:
            assert parsed_date == datetime.datetime.fromisoformat(date_string[:19])