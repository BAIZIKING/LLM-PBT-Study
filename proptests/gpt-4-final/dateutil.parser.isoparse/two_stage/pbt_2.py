from hypothesis import given, strategies as st
from dateutil.parser import isoparse
from datetime import datetime
from dateutil.tz import tzoffset, tzutc

# Strategy for generating valid ISO-8601 strings
iso_strings = st.text(min_size=10, max_size=20, alphabet='0123456789:-TZ')

# Strategy for generating invalid ISO-8601 strings
invalid_strings = st.text(min_size=10, max_size=20)

@given(iso_strings)
def test_isoparse_type_correctness(iso_str):
    try:
        result = isoparse(iso_str)
        assert isinstance(result, datetime)
    except ValueError:
        pass  # Skip invalid strings

@given(iso_strings)
def test_isoparse_defaults(iso_str):
    try:
        result = isoparse(iso_str)
        if 'T' not in iso_str:
            assert result.hour == 0 and result.minute == 0 and result.second == 0
    except ValueError:
        pass  # Skip invalid strings

@given(iso_strings)
def test_isoparse_timezone(iso_str):
    try:
        result = isoparse(iso_str)
        if 'Z' in iso_str:
            assert isinstance(result.tzinfo, tzutc)
        elif '+' in iso_str or '-' in iso_str:
            assert isinstance(result.tzinfo, tzoffset)
    except ValueError:
        pass  # Skip invalid strings

@given(invalid_strings)
def test_isoparse_error_handling(inv_str):
    try:
        result = isoparse(inv_str)
        assert False, "Expected ValueError for invalid ISO-8601 strings"
    except ValueError:
        pass  # Expected error

@given(st.tuples(iso_strings, iso_strings))
def test_isoparse_consistency(iso_strs):
    try:
        result1 = isoparse(iso_strs[0])
        result2 = isoparse(iso_strs[1])
        assert result1 == result2, "Expected the same datetime for identifcal valid ISO-8601 strings"
    except ValueError:
        pass  # Skip if either string is invalid
# End program