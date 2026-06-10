from hypothesis import given, strategies as st
import dateutil

# Define strategies for generating input data
time_strings = st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126))
tzinfos = st.dictionaries(keys=st.text(), values=st.integers())
defaults = st.datetimes()

@given(timestr=time_strings, parserinfo=st.none() | st.builds(dateutil.parser.parserinfo),
       default=st.none() | defaults, ignoretz=st.booleans(), tzinfos=st.none() | tzinfos, 
       dayfirst=st.none() | st.booleans(), yearfirst=st.none() | st.booleans(),
       fuzzy=st.booleans(), fuzzy_with_tokens=st.booleans())
def test_dateutil_parser_parse_properties(timestr, parserinfo, default, ignoretz, tzinfos, dayfirst, yearfirst, fuzzy, fuzzy_with_tokens):
    try:
        result = dateutil.parser.parse(timestr, parserinfo, default=default, ignoretz=ignoretz, tzinfos=tzinfos,
                                      dayfirst=dayfirst, yearfirst=yearfirst, fuzzy=fuzzy, fuzzy_with_tokens=fuzzy_with_tokens)
        # Property 1: Output Type
        assert isinstance(result, dateutil.parser.datetime.datetime) or \
               (fuzzy_with_tokens and isinstance(result, tuple) and 
                isinstance(result[0], dateutil.parser.datetime.datetime))
        
        # Property 2: Timezones
        if not ignoretz and (tzinfos is not None or "GMT" in timestr or "+" in timestr or "-" in timestr):
            assert result.tzinfo is not None 
        
        # Property 3: Date Components
        assert 1 <= result.year <= 9999
        assert 1 <= result.month <= 12
        assert 1 <= result.day <= 31 
        
        # Property 4: Fuzzy Parsing 
        if fuzzy:
            # Assuming fuzzy parsing succeeds, we can't assert much beyond basic date validity
            assert 1 <= result.year <= 9999
            assert 1 <= result.month <= 12
            assert 1 <= result.day <= 31 
        
        # Property 5: Default Parameter 
        if default is not None:
            for attr in ["year", "month", "day", "hour", "minute", "second", "microsecond"]:
                if getattr(result, attr) == getattr(default, attr):
                    assert timestr.find(str(getattr(result, attr))) == -1
                
    except dateutil.parser.ParserError:
        # Ignore parsing errors
        pass 
# End program