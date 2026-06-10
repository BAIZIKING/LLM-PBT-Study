from hypothesis import given, strategies as st
import dateutil

# Define strategies for generating test data
date_strings = st.text(alphabet=st.characters(blacklist_categories=("C", "Z")), min_size=1)
tz_strings = st.sampled_from(["UTC", "EST", "CST", "PST", "BRST"])
tzinfos_dict = st.dictionaries(keys=tz_strings, values=st.integers(min_value=-14400, max_value=14400))

@given(date_strings, st.booleans(), st.booleans(), tzinfos_dict, st.datetimes(), st.booleans())
def test_dateutil_parser_parse_output_type(timestr, ignoretz, yearfirst, tzinfos, default, fuzzy):
    try:
        result = dateutil.parser.parse(timestr, ignoretz=ignoretz, yearfirst=yearfirst, tzinfos=tzinfos, default=default, fuzzy=fuzzy)
        if fuzzy_with_tokens:
            assert isinstance(result, tuple) and isinstance(result[0], datetime.datetime)
        else:
            assert isinstance(result, datetime.datetime)
    except dateutil.parser.ParserError:
        pass  # Ignore parsing errors for this property

@given(date_strings, st.booleans(), tzinfos_dict)
def test_dateutil_parser_parse_timezone(timestr, ignoretz, tzinfos):
    try:
        result = dateutil.parser.parse(timestr, ignoretz=ignoretz, tzinfos=tzinfos)
        if ignoretz:
            assert result.tzinfo is None
        else:
            # Assuming the input string has a timezone, it should be parsed 
            assert result.tzinfo is not None 
    except dateutil.parser.ParserError:
        pass 

@given(date_strings, st.booleans(), st.booleans(), tzinfos_dict)
def test_dateutil_parser_parse_date_components(timestr, ignoretz, yearfirst, tzinfos):
    try:
        result = dateutil.parser.parse(timestr, ignoretz=ignoretz, yearfirst=yearfirst, tzinfos=tzinfos)
        assert 1 <= result.year <= 9999
        assert 1 <= result.month <= 12
        assert 1 <= result.day <= calendar.monthrange(result.year, result.month)[1]
    except dateutil.parser.ParserError:
        pass  

@given(date_strings, st.datetimes(), st.booleans())
def test_dateutil_parser_parse_fuzzy_parsing(timestr, default, fuzzy):
    try:
        result = dateutil.parser.parse(timestr, default=default, fuzzy=fuzzy)
        # Assuming fuzzy parsing is successful, a valid date should be generated 
        assert 1 <= result.year <= 9999
        assert 1 <= result.month <= 12
        assert 1 <= result.day <= calendar.monthrange(result.year, result.month)[1] 
    except dateutil.parser.ParserError:
        pass 

@given(date_strings, st.datetimes())
def test_dateutil_parser_parse_default_values(timestr, default):
    try:
        result = dateutil.parser.parse(timestr, default=default)
        # Check if missing components are taken from the default 
        if not timestr.strip():  
            assert result == default
        else:
            for attr in ["year", "month", "day", "hour", "minute", "second", "microsecond"]:
                if getattr(result, attr) != getattr(default, attr): 
                    break  # Found a component that differs, meaning the default was used
            else:
                assert False, "Default values not used when they should have been"
    except dateutil.parser.ParserError:
        pass 
# End program