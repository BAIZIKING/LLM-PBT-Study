from hypothesis import given, strategies as st
from dateutil.parser import parse
import datetime

# Property 1: Datetime Object Given Valid Input
@given(st.text(min_size=10, max_size=10))
def test_datetime_object_given_valid_input(timestr):
    date = parse(timestr)
    assert isinstance(date, datetime.datetime)

# Property 2: Ignore Timezone Flag
@given(st.text(min_size=10, max_size=10))
def test_ignore_timezone_flag(timestr):
    date = parse(timestr, ignoretz=True)
    assert date.tzinfo is None

# Property 3: Timezone Information Mapping
@given(st.text(min_size=10, max_size=10), st.dictionaries(st.text(), st.integers()))
def test_timezone_information_mapping(timestr, tzinfos):
    date = parse(timestr, tzinfos=tzinfos)
    assert date.tzinfo is not None

# Property 4: Fuzzy Parsing
@given(st.text(min_size=20))
def test_fuzzy_parsing(timestr):
    date = parse(timestr, fuzzy=True)
    assert isinstance(date, datetime.datetime)
    
# Property 5: Fuzzy Parsing with Tokens
@given(st.text(min_size=20))
def test_fuzzy_parsing_with_tokens(timestr):
    date, tokens = parse(timestr, fuzzy_with_tokens=True)
    assert isinstance(date, datetime.datetime)
    assert isinstance(tokens, tuple)
# End program