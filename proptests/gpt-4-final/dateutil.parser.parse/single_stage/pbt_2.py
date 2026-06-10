from hypothesis import given, example, strategies as st
from dateutil.parser import parse

@given(st.text(), st.booleans(), st.booleans(), st.booleans(), st.booleans())
def test_dateutil_parser_parse(timestr, fuzzy, dayfirst, yearfirst, ignoretz):
    try:
        result = parse(timestr, fuzzy=fuzzy, dayfirst=dayfirst, yearfirst=yearfirst, ignoretz=ignoretz)
        assert isinstance(result, datetime.datetime) or (isinstance(result, tuple) and isinstance(result[0], datetime.datetime))
    except ValueError:
        assert not re.match('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', timestr)  # if ValueError raises, it's due to invalid timestr