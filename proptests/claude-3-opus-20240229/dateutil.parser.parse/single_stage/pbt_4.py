from hypothesis import given, strategies as st
from dateutil.parser import parse
from dateutil.tz import gettz
import datetime

# Generate a wide variety of string formats including common cases, 
# ambiguous cases (e.g. 01/02/03), inclusion/omission of time components, 
# timezone names and offsets, invalid formats, and long strings.
# Also generate various combinations of keyword arguments to test
# the different parsing options and edge cases.
@given(
    timestr=st.one_of(
        st.dates().map(str),
        st.times().map(str), 
        st.datetimes().map(str),
        st.just("Today"),
        st.just("January 1, 2047 at 8:21:00AM"),
        st.from_regex(r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}"),
        st.from_regex(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}"),  
        st.from_regex(r"\d{1,2}[-/]\d{1,2}[-/]\d{1,2}"),
        st.from_regex(r"[^\d\-\/]{10}"),
        st.from_regex(r"[^\d\-\/]{100}")
    ),
    default=st.one_of(st.none(), st.datetimes()),
    ignoretz=st.booleans(),
    tzinfos=st.one_of(
        st.none(), 
        st.dictionaries(st.text(), st.one_of(st.integers(), st.timezones())),
        st.functions(like=(lambda tzname, offset: gettz("America/Chicago")))
    ),
    dayfirst=st.one_of(st.none(), st.booleans()), 
    yearfirst=st.one_of(st.none(), st.booleans()),
    fuzzy=st.booleans(),
    fuzzy_with_tokens=st.booleans()
)
def test_dateutil_parser_parse(timestr, default, ignoretz, tzinfos, 
                               dayfirst, yearfirst, fuzzy, fuzzy_with_tokens):

    # If fuzzy_with_tokens=True, check the return value is a tuple with a datetime
    # object as the first element. The second element should be a tuple containing
    # portions of the string that were ignored. 
    if fuzzy_with_tokens:
        assert isinstance(parse(timestr, default=default, ignoretz=ignoretz, 
                       tzinfos=tzinfos, dayfirst=dayfirst, yearfirst=yearfirst, 
                       fuzzy=fuzzy, fuzzy_with_tokens=fuzzy_with_tokens), tuple)
        assert isinstance(parse(timestr, default=default, ignoretz=ignoretz, 
                       tzinfos=tzinfos, dayfirst=dayfirst, yearfirst=yearfirst, 
                       fuzzy=fuzzy, fuzzy_with_tokens=fuzzy_with_tokens)[0], datetime.datetime)
        assert isinstance(parse(timestr, default=default, ignoretz=ignoretz, 
                       tzinfos=tzinfos, dayfirst=dayfirst, yearfirst=yearfirst, 
                       fuzzy=fuzzy, fuzzy_with_tokens=fuzzy_with_tokens)[1], tuple)

    # Otherwise, check the return value is a datetime.datetime object
    else:
        assert isinstance(parse(timestr, default=default, ignoretz=ignoretz, 
                       tzinfos=tzinfos, dayfirst=dayfirst, yearfirst=yearfirst, 
                       fuzzy=fuzzy, fuzzy_with_tokens=fuzzy_with_tokens), datetime.datetime)
        
    # If ignoretz=True, check that the returned datetime object is naive
    if ignoretz:
        assert parse(timestr, default=default, ignoretz=ignoretz, 
                       tzinfos=tzinfos, dayfirst=dayfirst, yearfirst=yearfirst, 
                       fuzzy=fuzzy, fuzzy_with_tokens=fuzzy_with_tokens).tzinfo is None

# End program        