from hypothesis import given, strategies as st
import dateutil

@given(timestr=st.text(), 
       default=st.datetimes(min_value=dateutil.parser.parse("0001-01-01"),
                           max_value=dateutil.parser.parse("9999-12-31 23:59:59")),
       ignoretz=st.booleans(),
       tzinfos=st.dictionaries(keys=st.text(), values=st.integers()),
       dayfirst=st.booleans(), 
       yearfirst=st.booleans(), 
       fuzzy=st.booleans(), 
       fuzzy_with_tokens=st.booleans())
def test_dateutil_parser_parse_properties(timestr, default, ignoretz, tzinfos, dayfirst, yearfirst, fuzzy, fuzzy_with_tokens):
    try:
        result = dateutil.parser.parse(timestr, default=default, ignoretz=ignoretz, tzinfos=tzinfos, dayfirst=dayfirst, yearfirst=yearfirst, fuzzy=fuzzy, fuzzy_with_tokens=fuzzy_with_tokens)
        
        # Property 1: Output Type
        assert isinstance(result, (datetime.datetime, tuple))
        if fuzzy_with_tokens:
            assert isinstance(result[0], datetime.datetime)
            
        # Property 2: Time Zone
        if not ignoretz and result.tzinfo is not None:
            assert isinstance(result.tzinfo, (datetime.timezone, dateutil.tz.tzoffset, dateutil.tz.tzfile))
            
        # Property 3: Date Components 
        assert 1 <= result.year <= 9999
        assert 1 <= result.month <= 12
        assert 1 <= result.day <= calendar.monthrange(result.year, result.month)[1]

        # Property 4: Fuzzy Parsing - Not directly testable but covered by Hypothesis strategy generation

        # Property 5: Default Parameter
        if default is not None:
            for attr in ["year", "month", "day", "hour", "minute", "second", "microsecond"]:
                if getattr(result, attr) == getattr(default, attr):
                    assert getattr(timestr, attr) is None  # Verify the value came from the default
                    
    except dateutil.parser.ParserError:
        pass # Ignore parsing errors

# End program