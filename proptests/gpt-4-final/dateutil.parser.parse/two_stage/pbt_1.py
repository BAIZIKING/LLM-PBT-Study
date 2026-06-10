from hypothesis import given, strategies as st
from dateutil.parser import parse
import datetime

@given(st.text(), st.booleans(), st.datetimes(), st.booleans(), st.booleans(), st.booleans(), st.booleans())
def test_dateutil_parse_properties(timestr, ignoretz, default, dayfirst, yearfirst, fuzzy, fuzzy_with_tokens):
    
    # Property 1: Validate the return type
    result = parse(timestr, ignoretz=ignoretz, default=default, dayfirst=dayfirst, yearfirst=yearfirst, 
                   fuzzy=fuzzy, fuzzy_with_tokens=fuzzy_with_tokens)
    if fuzzy_with_tokens:
        assert isinstance(result, tuple)
        assert isinstance(result[0], datetime.datetime)
    else:
        assert isinstance(result, datetime.datetime)
    
    # Property 2: Check timezone information handling
    if ignoretz:
        assert result.tzinfo is None
    
    # Property 3: Test 'default' parameter handling
    if default:
        assert (result.year, result.month, result.day) == (default.year, default.month, default.day)
    
    # Property 4: Omitted as it requires custom ambiguous date strings for testing
    
    # Property 5: Validate 'fuzzy_with_tokens' handling
    if fuzzy_with_tokens:
        assert isinstance(result[1], tuple)