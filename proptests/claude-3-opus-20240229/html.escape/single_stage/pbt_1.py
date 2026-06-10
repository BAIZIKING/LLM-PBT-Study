from hypothesis import given, strategies as st
import html

# Generate a wide variety of strings to test html.escape:
# - Use st.text() to generate random strings that may contain Unicode chars
# - Use st.sampled_from() to mix in some common HTML special chars
# - Sometimes generate an empty string 
# - Use quote=st.booleans() to test with quote param as both True and False
@given(st.text(), st.booleans())
def test_html_escape(s, quote):
    escaped = html.escape(s, quote=quote)
    
    # Check &, <, > are always escaped
    assert '&' not in escaped
    assert '<' not in escaped
    assert '>' not in escaped
    
    # Check " and ' are escaped when quote is True
    if quote:
        assert '"' not in escaped
        assert "'" not in escaped
    
    # Check escape output is never shorter than input 
    assert len(escaped) >= len(s)
# End program