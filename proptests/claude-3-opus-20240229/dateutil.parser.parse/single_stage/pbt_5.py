from hypothesis import given, strategies as st
from dateutil.parser import parse
from datetime import datetime

# Generate a wide variety of string formats that could represent dates/times.
# Include common separators like /, -, and whitespace.
# Generate strings with a mix of numeric and non-numeric characters.
# Generate standalone years, months, days, and times.
# Generate strings with and without timezone info.
# Generate strings that use month names and abbreviations.
# Generate ambiguous dates like 01/02/03 to test dayfirst/yearfirst handling.
@given(st.data())
def test_dateutil_parser_parse(data):
    date_string = data.draw(st.one_of(
        st.dates().map(str),
        st.datetimes().map(str),
        st.times().map(str),
        st.from_regex(r"\d{1,4}[-/\s]\d{1,2}[-/\s]\d{1,4}"),
        st.from_regex(r"\d{1,2}[-/\s]\d{1,2}[-/\s]\d{2,4}"),
        st.from_regex(r"\d{4,14}"),
        st.from_regex(r"\d{1,2}:\d{2}(:\d{2})?(\s?[aApP][mM])?"),
        st.from_regex(r"[a-zA-Z]{3,9}\s+\d{1,2},?\s+\d{4}"),
        st.from_regex(r"\d{1,2}\s+[a-zA-Z]{3,9}\s+\d{4}"),
    ))

    default = data.draw(st.none() | st.datetimes())
    ignoretz = data.draw(st.booleans())
    tzinfos = data.draw(st.none() | st.dictionaries(st.text(), st.timezones()))
    dayfirst = data.draw(st.none() | st.booleans())
    yearfirst = data.draw(st.none() | st.booleans())
    fuzzy = data.draw(st.booleans())
    fuzzy_with_tokens = data.draw(st.booleans())
    
    result = parse(date_string, default=default, ignoretz=ignoretz, tzinfos=tzinfos, 
                   dayfirst=dayfirst, yearfirst=yearfirst, fuzzy=fuzzy, fuzzy_with_tokens=fuzzy_with_tokens)
    
    # Check that the result is a datetime object or a tuple with a datetime object
    if fuzzy_with_tokens:
        assert isinstance(result, tuple)
        assert isinstance(result[0], datetime)
        assert isinstance(result[1], tuple)
    else:
        assert isinstance(result, datetime)
        
    # Check that unspecified elements match the default
    if default is not None:
        if not date_string:
            assert result == default
        for attr in ['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond']:
            if not getattr(result, attr):
                assert getattr(result, attr) == getattr(default, attr)
                
    # Check that timezone is UTC if ignoretz is True
    if ignoretz:
        assert result.tzinfo is None
        
# End program