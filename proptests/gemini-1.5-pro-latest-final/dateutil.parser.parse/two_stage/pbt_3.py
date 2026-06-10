from hypothesis import given, strategies as st
import dateutil.parser

# Define strategies for generating test data
time_strs = st.text(alphabet=st.characters(blacklist_categories=('C', 'Z')), min_size=1)  # Avoid control characters and separators
tz_infos = st.dictionaries(keys=st.text(), values=st.integers(min_value=-12*3600, max_value=14*3600))  # Time zone offsets in seconds
defaults = st.datetimes() 

@given(time_str=time_strs, parserinfo=st.none() | st.builds(dateutil.parser.parserinfo),
       tzinfos=tz_infos, default=defaults, ignoretz=st.booleans(), 
       dayfirst=st.booleans() | st.none(), yearfirst=st.booleans() | st.none(), 
       fuzzy=st.booleans(), fuzzy_with_tokens=st.booleans())
def test_dateutil_parser_parse_properties(time_str, parserinfo, tzinfos, default, ignoretz, dayfirst, yearfirst, fuzzy, fuzzy_with_tokens):
    try:
        result = dateutil.parser.parse(timestr=time_str, parserinfo=parserinfo, tzinfos=tzinfos, default=default, ignoretz=ignoretz,
                                       dayfirst=dayfirst, yearfirst=yearfirst, fuzzy=fuzzy, fuzzy_with_tokens=fuzzy_with_tokens)
        
        # Property 1: Output Type
        assert isinstance(result, dateutil.parser._parser.ParserError) or isinstance(result, (tuple, datetime.datetime)) 

        if not isinstance(result, dateutil.parser._parser.ParserError):
            # Successful parsing
            if fuzzy_with_tokens:
                dt_result, _ = result
            else:
                dt_result = result

            # Property 2: Time Zone
            if not ignoretz and dt_result.tzinfo is not None:
                assert isinstance(dt_result.tzinfo, (dateutil.tz.tzoffset, dateutil.tz.tzfile))

            # Property 3: Date Components
            assert 1 <= dt_result.month <= 12
            assert 1 <= dt_result.day <= 31  # Assuming valid date combinations 

            # Property 4: Fuzzy Parsing
            if fuzzy or fuzzy_with_tokens:
                if "today" in time_str.lower():
                    assert dt_result.date() == datetime.date.today() 

            # Property 5: Default Parameter
            if isinstance(default, datetime.datetime):
                for attr in ["year", "month", "day", "hour", "minute", "second", "microsecond"]:
                    if getattr(dt_result, attr) != getattr(default, attr):
                        # At least one element should have been overridden
                        break
                else:
                    assert False, "Default datetime not overridden by parsed string"
    except OverflowError:
        # Gracefully handle overflows, which can occur with very large inputs
        pass
# End program