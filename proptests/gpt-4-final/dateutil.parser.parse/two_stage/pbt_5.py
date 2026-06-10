from hypothesis import given, strategies as st
from dateutil.parser import parse
import pytest
import datetime

# Test 1: DataType Test 
@given(st.text())
def test_dateutil_parser_parse_return_type(timestr):
    result = parse(timestr)
    assert isinstance(result, datetime.datetime)

# Test 2: Size of tuples 
@given(st.text())
def test_dateutil_parser_parse_tuple_size(timestr):
    result, _ = parse(timestr, fuzzy_with_tokens=True)
    assert isinstance(result, tuple)
    assert len(result) == 2

# Test 3: Date correctness
@given(st.text(min_size=10, max_size=10))
def test_dateutil_parser_parse_date_correctness(timestr):
    result = parse(timestr)
    input_date = datetime.datetime.strptime(timestr, '%Y-%m-%d')
    assert result.date() == input_date.date()

# Test 4: Time zone verification
@given(st.text())
def test_dateutil_parser_parse_timezone(timestr):
    tzinfos = {"EST": -18000}
    result = parse(timestr + ' EST', tzinfos=tzinfos)
    assert result.tzinfo.utcoffset(None).total_seconds() == tzinfos['EST']

# Test 5: Error Raising
@given(st.text(min_size=11, max_size=11))
def test_dateutil_parser_parse_errors(timestr):
    with pytest.raises(ValueError):
        parse(timestr)

# End program