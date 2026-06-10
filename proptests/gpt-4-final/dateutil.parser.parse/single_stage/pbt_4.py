from hypothesis import given, strategies as st
from dateutil.parser import parse

@given(date_str=st.text(min_size=10, max_size=30),
       default=st.datetimes(),
       ignoretz=st.booleans(),
       dayfirst=st.booleans(),
       yearfirst=st.booleans(),
       fuzzy=st.booleans()
)
def test_dateutil_parser_parse(date_str, default, ignoretz, dayfirst, yearfirst, fuzzy):
    try:
        parsed_date = parse(date_str, default=default, ignoretz=ignoretz, dayfirst=dayfirst, yearfirst=yearfirst, fuzzy=fuzzy)
        assert parsed_date >= default
        if ignoretz:
            assert parsed_date.tzinfo is None
    except ValueError:
        assert True
# End program