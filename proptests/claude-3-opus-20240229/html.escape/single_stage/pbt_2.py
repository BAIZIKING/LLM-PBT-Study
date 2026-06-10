from hypothesis import given, strategies as st
from html import escape

# Summary: Generate a wide variety of strings to test html.escape.
# Include plain strings, strings with HTML special chars, empty string.
# Check that & < > are always escaped. If quote=True, check that ' " are escaped too.
@given(st.text())
def test_html_escape(s):
    escaped = escape(s)
    assert '&' not in escaped
    assert '<' not in escaped 
    assert '>' not in escaped
    if '"' in s:
        assert '&quot;' in escaped
    if "'" in s:  
        assert '&#x27;' in escaped
        
# End program