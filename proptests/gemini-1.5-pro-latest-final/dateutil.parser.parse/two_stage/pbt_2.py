from hypothesis import given, strategies as st
import dateutil.parser

# Define strategies for generating test data
timestr_strategy = st.text(alphabet=st.characters(blacklist_categories=("C",)), min_size=1)
tzinfo_strategy = st.dictionaries(keys=st.text(), values=st.integers(min_value=-86400, max_value=86400))

@given(timestr=timestr_strategy, tzinfos=tzinfo_strategy, ignoretz=st.booleans(), 
       dayfirst=st.booleans(), yearfirst=st.booleans(), fuzzy=st.booleans(),
       fuzzy_with_tokens=st.booleans())
def test_dateutil_parser_parse_output_type(timestr, tzinfos, ignoretz, dayfirst, yearfirst, fuzzy, fuzzy_with_tokens):
    try:
        result = dateutil.parser.parse(timestr, tzinfos=tzinfos, ignoretz=ignoretz, dayfirst=dayfirst, yearfirst=yearfirst, fuzzy=fuzzy, fuzzy_with_tokens=fuzzy_with_tokens)
        if fuzzy_with_tokens:
            assert isinstance(result, tuple) and isinstance(result[0], datetime.datetime)
        else:
            assert isinstance(result, datetime.datetime)
    except dateutil.parser.ParserError:
        pass  # Ignore parsing errors for this property

@given(timestr=timestr_strategy, tzinfos=tzinfo_strategy)
def test_dateutil_parser_parse_timezone(timestr, tzinfos):
    try:
        result = dateutil.parser.parse(timestr, tzinfos=tzinfos)
        if result.tzinfo is not None:
            assert isinstance(result.tzinfo, (datetime.timezone, dateutil.tz.tzinfo))
    except dateutil.parser.ParserError:
        pass

@given(timestr=timestr_strategy)
def test_dateutil_parser_parse_date_components(timestr):
    try:
        result = dateutil.parser.parse(timestr)
        assert 1 <= result.month <= 12
        assert 1 <= result.day <= 31  # Assuming valid date parsing
    except dateutil.parser.ParserError:
        pass

@given(timestr=timestr_strategy)
def test_dateutil_parser_parse_time_components(timestr):
    try:
        result = dateutil.parser.parse(timestr)
        assert 0 <= result.hour <= 23
        assert 0 <= result.minute <= 59
        assert 0 <= result.second <= 59
        assert 0 <= result.microsecond <= 999999
    except dateutil.parser.ParserError:
        pass

@given(timestr=timestr_strategy)
def test_dateutil_parser_parse_fuzzy(timestr):
    try:
        result, fuzzy_tokens = dateutil.parser.parse(timestr, fuzzy_with_tokens=True)
        # Check that fuzzy parsing was successful 
        assert isinstance(result, datetime.datetime)
        # Check that fuzzy tokens are strings 
        assert all(isinstance(token, str) for token in fuzzy_tokens)
    except dateutil.parser.ParserError:
        pass

# End program 