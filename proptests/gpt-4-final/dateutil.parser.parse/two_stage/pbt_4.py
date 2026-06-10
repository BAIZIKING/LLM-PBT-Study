from hypothesis import given, strategies as st
from dateutil.parser import parse, ParserError
from dateutil.tz import gettz
from datetime import datetime

@given(timestr=st.text(), 
       default=st.none() | st.datetimes(), 
       ignoretz=st.booleans(), 
       tzinfos=st.none() | st.dictionaries(keys=st.text(), values=st.integers()), 
       dayfirst=st.booleans(), 
       yearfirst=st.booleans(), 
       fuzzy=st.booleans(), 
       fuzzy_with_tokens=st.booleans())
def test_dateutil_parser_parse_property(timestr, default, ignoretz, tzinfos, dayfirst, yearfirst, fuzzy, fuzzy_with_tokens):
    try:
        result = parse(timestr, 
               default=default, 
               ignoretz=ignoretz, 
               tzinfos=tzinfos, 
               dayfirst=dayfirst, 
               yearfirst=yearfirst, 
               fuzzy=fuzzy, 
               fuzzy_with_tokens=fuzzy_with_tokens)
        
        # property 1
        assert isinstance(result, datetime)
        
        # property 2
        if ignoretz:
            assert result.tzinfo is None
            
        # property 3
        if tzinfos and not ignoretz:
            assert result.tzinfo is not None

        # property 4
        if dayfirst or yearfirst:
            assert isinstance(result, datetime)
            
        # property 5
        assert isinstance(result, datetime) or result[0] == (u'Today is ', u' ', u'at ')

    except (ParserError, OverflowError) as e:
        pass # For now lets swallow the expected exceptions, we could also analyze the message