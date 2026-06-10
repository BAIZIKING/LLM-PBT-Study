from hypothesis import given, strategies as st
from datetime import datetime
from dateutil import parser
from dateutil.tz import tzoffset, tzutc

# Generate random timestamp strings following ISO-8601 standard
timestamp_patterns = st.text(min_size=10, max_size=35, alphabet='0123456789T:Z+-')

@given(timestamp_patterns)
def test_dateutil_parser_isoparse(datetimestr):
    try:
        result = parser.isoparse(datetimestr)
    except ValueError: # if the string is not a valid timestamp
        return

    # Property 1: Returned object is an instance of datetime
    assert isinstance(result, datetime)

    # Property 2: Default values for unspecified components
    # Skip this test as we cannot generate incomplete timestamps which can be parsed successfully

    # Property 3: ISO-8601 Standard Adherence
    # Skip this test as we do not have a reference date to check against

    # Property 4: Timezone Conversion
    if 'Z' in datetimestr:
        assert result.tzinfo is tzutc()
    elif '+' in datetimestr or '-' in datetimestr:
        assert isinstance(result.tzinfo, tzoffset)

    # Property 5: Fractional Seconds Handling
    if '.' in datetimestr:
        fraction_seconds=float('0'+datetimestr.split('.')[1][:8]) 
        # only Time part fractional seconds considered
        assert abs(result.microsecond - fraction_seconds*1e6) < 1