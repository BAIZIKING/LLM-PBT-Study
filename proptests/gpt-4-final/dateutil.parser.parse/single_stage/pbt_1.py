from hypothesis import given, strategies as st
from dateutil.parser import parse, ParserError
from datetime import datetime

@given(
    timestr=st.text(),
    ignoretz=st.booleans(),
    dayfirst=st.booleans(),
    yearfirst=st.booleans(),
    fuzzy=st.booleans(),
    fuzzy_with_tokens=st.booleans()
)
def test_dateutil_parser_parse(timestr, ignoretz, dayfirst, yearfirst, fuzzy, fuzzy_with_tokens):
    try:
        result = parse(timestr, 
                        ignoretz=ignoretz, 
                        dayfirst=dayfirst, 
                        yearfirst=yearfirst, 
                        fuzzy=fuzzy, 
                        fuzzy_with_tokens=fuzzy_with_tokens
                       )
        assert isinstance(result, datetime) or \
               (isinstance(result, tuple) and isinstance(result[0], datetime))
    except ParserError:
        pass  # Parse errors are expected with some inputs, just ignore them